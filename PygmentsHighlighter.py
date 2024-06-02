#this module uses text mate to parse the code for highlighting
#syntax
from PySide6 import QtGui, QtCore
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatter import Formatter


#TODO: operators, delimiters, numbers, braces, brackets

KEYWORDS_PURPLE = ['as', 'assert', 'async', 'await', 'break', 'continue', 'del', 'elif', 
            'else', 'except', 'finally', 'for', 'from', 'if', 'import', 
            'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']

KEYWORDS_BLUE = ['False', 'None', 'True', 'and','lambda','not', 'or','is', 'def', 'nonlocal', 'class', 
        'global', 'in']

STYLE = {
    "keyword_p": "#7A6AC0",#pastel purple
    'keyword_b': "#2666CB",#pastel blue
    'string' : "#AC9178",#pastel brown
    'comment': "#6A9955",#olive drab
    "class_name" : "#34BCB0",#pastel green, modules in the import statements are also this color
    "function_name" : "#DCDC9D",#pastel yellow
    "variable_name" : "#50B9FE",#sky blue
    "defualt_parentheses" : "#1F1F1F",#gold
    "format_string" : "#4FC1FF",#pastel blue, (f'somestring') for the f
    "regex_string" : "#D16969",#salmon, (r'\bself\b') for the r
}

class QFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        Formatter.__init__(self, *args, **kwargs)
        self.data = []

    def format(self, tokensource, outfile):
        for ttype, value in tokensource:
            self.data.append((ttype, value))

class PygmentsHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QtGui.QTextDocument) -> None:
        super().__init__(parent)
        self.lexer = PythonLexer()
        self.formatter = QFormatter()
        self.function_names = set()
        self.class_names = set()
        self.module_names = set()
        self.variable_names = set()
        self.multitline_open = False#used to track multiline strings and comments

    def highlightBlock(self, text: str | None) -> None:
        if text is None:
            return
        
        if self.previousBlockState() == 1:#the previous block whats to stay open
            self.multitline_open = True

        # Reset current block state
        self.setCurrentBlockState(0)
        
        highlight(text, self.lexer, self.formatter)

        # print("formatter data", self.formatter.data)
        self.applyHighlighting(text)

        # Check if the current block contains the end of a multi-line string
        if self.multitline_open:
            if self.endsMultilineString(text):
                self.multitline_open = False
            else:
                #keep the block open
                self.setCurrentBlockState(1)
    
    def endsMultilineString(self, text):
        return text.endswith('"""') or text.endswith("'''")


    def applyHighlighting(self, text):
        idx = 0
        offset = 0
        for ttype, value in self.formatter.data:
            # print("ttype", ttype, "value", value)
            length = len(value)
            # print("text length", length)
            # print("getting color")
            color = self.getColor(idx, ttype, value)
            if color:
                #text.index(value) causes weird behavior when a parameter is one character long,
                #it changes the color of that character throught the entire document
                #instead we use offset to track the token 'window' in the text
                self.setFormat(offset, length, self.makeFormat(color))
            idx += 1
            offset += length

        self.formatter.data = []

    def getColor(self, idx, ttype, value):
        # print("ttype in get_color", ttype, "value", value)
        if self.multitline_open:
            #we are on a new line of a multiline string, all of the tokens from here to the end need to be highlighted.
            if value in ('"""', "'''"):#end of the multiline string
                self.multitline_open = False
                self.setCurrentBlockState(0)
            #iterate through the rest of the tokens and set their colors
            return STYLE['string']

        if 'Keyword' in str(ttype):
            
            if value == 'import':
                self.handleImportStatement(idx)

            if value in KEYWORDS_PURPLE:
                return STYLE['keyword_p']
            elif value in KEYWORDS_BLUE:
                return STYLE['keyword_b']
            
        elif str(ttype) == 'Token.Name.Function':#only see Name.Function at definition
            # print("function name", value)
            self.function_names.add(value)#track it so we can add color to this symbol when it is used
            # print("function names", self.function_names)
            return STYLE['function_name']
        
        elif str(ttype) == 'Token.Name.Class':#only see Name.Function at definition
            # print("class name", value)
            self.class_names.add(value)#track it so we can add color to this symbol when it is used
            # print("class names", self.class_names)
            return STYLE['class_name']
        
        elif str(ttype) == "Token.Name.Namespace":#module names in import statements                     
            self.module_names.add(value)
            return STYLE['class_name']#VsCode uses the same colors as class names
        
        elif str(ttype) == 'Token.Name.Builtin.Pseudo':#self
            return STYLE['variable_name']

        elif str(ttype) == 'Token.Name.Function.Magic':#init
            return STYLE['function_name']
        
        elif str(ttype) == 'Token.Name.Builtin':#built in functions
            return STYLE['class_name']
        
        elif str(ttype) == 'Token.Name':#it could be a class name or function name
            # print("token.name", value)
            if value in self.function_names:
                return STYLE['function_name']
            elif value in self.class_names:
                return STYLE['class_name']
            elif value in self.module_names:
                return STYLE['class_name']
            #if it is not a function or class name it is a variable name
            # print("returning variable color")
            return STYLE['variable_name']
        
        elif 'String' in str(ttype):
            # print("string value", value)
            if value in ('"""', "'''"):
                self.setCurrentBlockState(1)#keep the block open
            return STYLE['string']
        
        elif 'Comment' in str(ttype):
            return STYLE['comment']
        
        # print("no color found")
        return None
    
    def handleImportStatement(self, idx: int):
        #if the value is import we need to add the module names to the class_names set
        #for some reason import statements like - "from module import name1, name2" - name1 and name2 
        # are not being highlighted as Token.Name.Namespace but as Token.Name, we add all of the symbols now
        #so that when its time to handle Token.Name we can color them correctly
        for i in range(idx+1, len(self.formatter.data)):
            # print("i", i, "data", self.formatter.data[i])
            if str(self.formatter.data[i][0]) == 'Token.Name':
                # print("adding module name", self.formatter.data[i][1])
                self.module_names.add(self.formatter.data[i][1])

    

    def makeFormat(self, color) -> QTextCharFormat:
        _format = QTextCharFormat()
        _format.setForeground(QColor(color))
        return _format
