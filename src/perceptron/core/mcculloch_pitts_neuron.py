from typing import Any
import numpy as np


class neuron:
    __matrix = [[]]

    class unit(object):
        structure: 'neuron'
        layer = 0
        identifier = 0
        value = 0
        parents = []
        children = []

        def __init__(self, layer: int, identifier: int, value: int, structure: 'neuron'):
            self.value = value
            self.layer = layer
            self.identifier=identifier
            self.structure = structure
        

        def set_parents(self, parents: ['neuron.unit']):
            for parent in parents:
                self.structure.__matrix[parent.layer,parent.identifier].add_child(self)
        def add_parent(self, parent: 'neuron.unit'):
            self.structure.__matrix[parent.layer,parent.identifier].add_child(self)
        def set_children(self, children: ['neuron.unit']):
            for child in children:
                self.structure.__matrix[child.layer,child.identifier].add_parent(self)
        def add_child(self, child: 'neuron.unit'):
            self.structure.__matrix[child.layer,child.identifier].add_parent(self)
        
    def fit(self,sensory_units:int = 64, association_units:int = 82, response_units:int = 2 ):
        self.__matrix = [[neuron.unit(0,i,0,self) for i in range(0,sensory_units)],
                    [neuron.unit(1,i,0,self) for i in range(0,association_units)],
                    [neuron.unit(2,i,0,self) for i in range(0,response_units)]]
        #for each sensory_units add up to 8 random children from the pool of association_units

    def sensory_units(self):
        #hard coded size
        return np.split(np.array([s_unit.value for s_unit in self.__matrix[0]]).T,8)

    def set_sensory_units(self, vals: [int]):
        if len(self.__matrix[0]) == len(vals):
            for s_unit, val in zip(self.__matrix[0], vals): s_unit.value = val
        else:
            print(len(self.__matrix[0]))
            print(len(vals))