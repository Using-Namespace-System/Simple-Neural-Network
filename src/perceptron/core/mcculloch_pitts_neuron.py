
__matrix = [[]]

class unit(int):
    layer = 0
    identifier = 0
    value = 0
    parents = []
    children = []
    def __init__(self, layer: int, identifier: int, value: int):
        self.layer = layer
        self.identifier = identifier
        self.value = value
    def __int__(self):
        return self.value
    def set_parents(self, parents: ["unit"]):
        for parent in parents:
            __matrix[parent.layer,parent.identifier].add_child(self)
    def add_parent(self, parent: ["unit"]):
         __matrix[parent.layer,parent.identifier].add_child(self)
    def set_children(self, children: ["unit"]):
        for child in children:
            __matrix[child.layer,child.identifier].add_parent(self)
    def add_child(self, child: "unit"):
         __matrix[child.layer,child.identifier].add_parent(self)
    
def __init__(self, sensory_units:int = 400, association_units:int = 512, response_units:int = 8 ):
    __matrix = [[unit(0,i,0) for i in range(0,sensory_units-1)],
                [unit(1,i,0) for i in range(0,association_units-1)],
                [unit(2,i,0) for i in range(0,response_units-1)]]
    #for each sensory_units add up to 40 random children from the pool of association_units