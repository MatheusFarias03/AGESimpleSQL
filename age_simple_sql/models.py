class Vertex:

    def __init__(self, label:str, properties:dict) -> None:
        self.label = label
        self.properties = properties

class Edge:

    def __init__(self, label:str, properties:dict, 
                 from_vertex:Vertex, to_vertex:Vertex) -> None:
        self.label = label
        self.properties = properties
        self.from_vertex = from_vertex
        self.to_vertex = to_vertex
