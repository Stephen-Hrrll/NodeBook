"""
This module implements functions for managing project files. Like saving work, load work,
and creating new projects.
"""

import json
from typing import Any, Dict
from PySide6 import QtWidgets
from Edge import Edge

class FileManager:
    def __init__(self, canvas = None):
        self.canvas = canvas

    
    def loadProject(self):
        # open a window to select the file path 
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open Project", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "r") as file:
                project = json.load(file)
                self.loadProjectFromDict(project)

    def loadProjectFromDict(self, project: Dict[str, Any]):
        # clear the canvas
        self.canvas.scene.clear()
        self.canvas.nodes = []
        self.canvas.edges = []

        # create the nodes
        for node_dict in project["nodes"]:
            node = self.canvas.createNode(node_dict)
            # node.nodes_within = self.create_nodes_within(node_dict["nodes_within"], node)
            # print("load project node:", node.getId())
            self.canvas.nodes.append(node)
            self.canvas.scene.addItem(node)

        # create the edges
        # print("project edges:", project["edges"])
        for edge_dict in project["edges"]:
            # print("edge_dict:", edge_dict)
            source_node = self.canvas.getNodeById(edge_dict["source_node_id"])
            dest_node = self.canvas.getNodeById(edge_dict["dest_node_id"])
            source_pin = source_node.outputPin()
            dest_pin = dest_node.inputPin()
            edge = Edge(source_pin, dest_pin, self.canvas)
            self.canvas.edges.append(edge)
            self.canvas.scene.addItem(edge)
        print("project loaded")
        print("looking at node id, for duplicates")
        for node in self.canvas.nodes:
            print("node id:", node.getId())
        
        print("looking at edge source and dest node id, for duplicates")
        for edge in self.canvas.edges:
            print("edge source node id:", edge.sourceNode().getId())
            print("edge dest node id:", edge.destNode().getId())


    def saveProject(self):
        #create a list of dictionarie of the nodes
        print("save project nodes:", len(self.canvas.nodes))
        print("save project edges:", len(self.canvas.edges))
        result_nodes = []
        for node in self.canvas.nodes:
            result_nodes.append(node.toDict())

        print("result:", result_nodes)

        #create a list of dictionaries of the edges
        result_edges = []
        for edge in self.canvas.edges:
            result_edges.append(edge.toDict())

        # open a window to select the file path and set the name to save the project
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save Project", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "w") as file:
                json.dump({"nodes": result_nodes, "edges": result_edges}, file, indent=4)
                print("Project saved to:", file_path)