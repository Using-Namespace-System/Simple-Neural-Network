from typing import Any
import numpy as np


class neuron:
    __matrix = [[]]

    class unit(object):
        layer = 0
        identifier = 0
        value = 0
        __parents: ['neuron.unit']
        __children: ['neuron.unit']
        __parent_mask: [int]

        def __init__(self, layer: int, identifier: int, value: int):
            self.value = value
            self.layer = layer
            self.identifier=identifier
        
        def set_parents(self, parents: ['neuron.unit']):
            for parent in parents:
                parent.add_child(self)
                self.__parents.append(parent)
        def add_parent(self, parent: 'neuron.unit', _mask: int):
            print(_mask,((parent.layer,parent.identifier),(self.layer,self.identifier)))
            print(parent)
            print(self)
            self.__parents.append(self,parent)
            print(((self.layer,self.identifier),self.__parent_mask))
            self.__parent_mask.append(_mask)
            print(((self.layer,self.identifier),self.__parent_mask))
            print(id(self.__parent_mask))
        def set_children(self, children: ['neuron.unit'], _parent_masks: [int]):
            if(len(children) == len(_parent_masks)):
                print("Size: " + str((len(children),len(_parent_masks))))
                for child, mask in zip(children, _parent_masks):
                    #print((child.layer,child.identifier))
                    child.add_parent(self,mask)
                    self.children.append(child)
            print("Size Mismach: " + str((len(children),len(_parent_masks))))
        def add_child(self, child: 'neuron.unit'):
            self.children.append(child)
        
        def input_signals(self):
            #return np.array([parent.value * mask for parent,mask in zip(self.parents, self.parent_mask)])
            return self.parents
        
    def fit(self,sensory_units:int = 64, association_units:int = 82, response_units:int = 2 ):
        self.__matrix = [[neuron.unit(0,i,0) for i in range(0,sensory_units)],
                    [neuron.unit(1,i,0) for i in range(0,association_units)],
                    [neuron.unit(2,i,0) for i in range(0,response_units)]]
        
        #for each sensory_units add up to 8 random children (half negative half positive) from the pool of association_units
        mask = np.full(8, 1)
        mask[:4] = -1
        for s_unit in self.__matrix[0]:
            np.random.shuffle(mask)
            children = np.random.choice(association_units, 8,replace=False)
            #print((s_unit.layer,s_unit.identifier))
            #print(children)
            #print(mask)
            #print([(child.layer,child.identifier) for child in np.array(self.__matrix[1])[children]])
            s_unit.set_children(np.array(self.__matrix[1])[children],mask)

    def sensory_units(self):
        #hard coded size
        return np.split(np.array([s_unit.value for s_unit in self.__matrix[0]]).T,8)

    def set_sensory_units(self, vals: [int]):
        if len(self.__matrix[0]) == len(vals):
            for s_unit, val in zip(self.__matrix[0], vals): s_unit.value = val
        else:
            print(len(self.__matrix[0]))
            print(len(vals))

    def association_units(self):
        return self.__matrix[1]