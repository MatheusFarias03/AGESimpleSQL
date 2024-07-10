class Vertex:

    def __init__(self, label:str, properties:dict) -> None:
        self.label = label
        self.properties = properties

    def get_label(self):
        return self.label
    
    def get_properties(self):
        return self.properties
    
    def set_label(self, label:str):
        self.label = label

    def set_properties(self, properties:dict):
        self.properties = properties