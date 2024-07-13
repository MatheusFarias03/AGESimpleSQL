from .utils import format_properties

class Vertex:

    def __init__(self, label:str, properties:dict = {}) -> None:
        self.label = label
        self.properties = properties
        self.cypher_format_props = format_properties(self.properties) if bool(self.properties) else {}

class Edge:

    def __init__(self, label:str, from_vertex:Vertex, to_vertex:Vertex, 
                 properties:dict = {}) -> None:
        self.label = label
        self.from_vertex = from_vertex
        self.to_vertex = to_vertex
        self.properties = properties
        self.cypher_format_props = format_properties(self.properties) if bool(self.properties) else {}
