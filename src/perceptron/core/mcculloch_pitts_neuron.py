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

        def __init__(self, layer: int, identifier: int, value: int):
            self.value = value
            self.layer = layer
            self.identifier=identifier
            self.__parents = []
            self.__children = []
        
        def set_parents(self, parents: ['neuron.unit']):
            for parent in parents:
                parent.add_child(self)
                self.__parents.append(parent)
        def add_parent(self, parent: 'neuron.unit'):
            self.__parents.append(parent)
        def set_children(self, children: ['neuron.unit']):
            for child in children:
                child.add_parent(self)
                self.__children.append(child)
        def add_child(self, child: 'neuron.unit'):
            self.children.append(child)

    class association_unit(unit):
        __parent_mask: [int]
        threshold = 0
        def __init__(self, *args, **kwargs):
            super(neuron.association_unit, self).__init__(*args, **kwargs)
            self.threshold = 0
            self.__parent_mask = []
        def add_parent(self, *args, _mask: int):
            super(neuron.association_unit, self).add_parent(*args)
            self.__parent_mask.append(_mask)
        def input_signals(self):
            return np.array([parent.value * mask for parent,mask in 
                             zip(self.__parents, self.__parent_mask)])
        def activation(self):
            return self.value >= self.threshold
        
    class sensory_unit(unit):
        def set_children(self, children: ['neuron.association_unit'], _parent_masks: [int]):
            for child, mask in zip(children, _parent_masks):
                child.add_parent(self,mask)
                self.__children.append(child)
        
    class response_unit(unit):
        __exclusion_mask: [bool]
        __inclusion_mask: [bool]
        def __init__(self, *args, **kwargs):
            super(neuron.association_unit, self).__init__(*args, **kwargs)
            self.__inclusion_mask = []
            self.__exclusion_mask = []
        
        

        
    def fit(self,sensory_units:int = 64, association_units:int = 82, response_units:int = 2 ):
        self.__matrix = [[neuron.sensory_unit(0,i,0) for i in range(0,sensory_units)],
                    [neuron.association_unit(1,i,0) for i in range(0,association_units)],
                    [neuron.unit(2,i,0) for i in range(0,response_units)]]
        
        #for each sensory_units add up to 8 random children (half negative half positive) from the pool of association_units
        mask = np.full(8, 1)
        mask[:4] = -1
        for s_unit in self.__matrix[0]:
            np.random.shuffle(mask)
            children = np.random.choice(association_units, 8,replace=False)
            s_unit.set_children(np.array(self.__matrix[1])[children],mask)
        #slice 82 association units into 4 non overlapping subsets 
        #one subset for each of two possible states for each response unit
        

    def sensory_units(self):
        #hard coded size
        return np.split(np.array([s_unit.value for s_unit in self.__matrix[0]]).T,8)

    def set_sensory_units(self, vals: [int]):
        if len(self.__matrix[0]) == len(vals):
            for s_unit, val in zip(self.__matrix[0], vals): s_unit.value = val
            for a_unit in self.__matrix[1]: a_unit.value = sum(a_unit.input_signals()) 
        else:
            print("Size Mismatch: " + str((len(self.__matrix[0]), len(vals))))

    def association_units(self):
        return np.array([a_unit.value for a_unit in self.__matrix[1]])
    