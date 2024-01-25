from typing import Any
import numpy as np
import math


class neuron:
    __matrix: [['neuron.unit']]
    __sensory_units: int
    __association_units: int
    __response_units: int

    class unit(object):

        layer: int
        identifier: int
        value: int
        __parents: ['neuron.unit']
        __children: ['neuron.unit']

        def __init__(self, layer: int, identifier: int, value: int):
            self.value = value
            self.layer = layer
            self.identifier=identifier
            self.__parents = []
            self.__children = []
        
        @property
        def parents(self):
                return self.__parents
        @parents.setter
        def set_parents(self, parents: ['neuron.unit']):
            for parent in parents:
                parent.add_child(self)
                self.__parents.append(parent)
        def add_parent(self, parent: 'neuron.unit'):
            self.__parents.append(parent)
        @property
        def children(self):
            return self.__children
        @children.setter
        def set_children(self, children: ['neuron.unit']):
            for child in children:
                child.add_parent(self)
                self.__children.append(child)
        def add_child(self, child: 'neuron.unit'):
            self.__children.append(child)

    class association_unit(unit):
        __excitatory_filter: [int]
        threshold: int
        def __init__(self, *args, **kwargs):
            super(neuron.association_unit, self).__init__(*args, **kwargs)
            self.threshold = 0
            self.__excitatory_filter = []
        def add_parent(self, *args, filter: int):
            super(neuron.association_unit, self).add_parent(*args)
            self.__excitatory_filter.append(filter)
        def input_signals(self):
            return np.array([parent.value * mask for parent,mask in 
                             zip(self.parents, self.__excitatory_filter)])
        def activation(self):
            return self.value >= self.threshold
        
    class sensory_unit(unit):
        def set_children(self, children: ['neuron.association_unit'], excitatory_filter: [int]):
            for child, filter in zip(children, excitatory_filter):
                child.add_parent(self,filter=filter)
                self.add_child(child)
        
    class response_unit(unit):
        __inclusion_mask: [bool]
        __exclusion_mask: [bool]
        
        def __init__(self, *args, **kwargs):
            super(neuron.response_unit, self).__init__(*args, **kwargs)
            self.__inclusion_mask = []
            self.__exclusion_mask = []
        def set_parents(self, parents: ['neuron.association_unit'], inclusions_exclusions: ([bool],[bool])):
            inclusions, exclusions = inclusions_exclusions
            for parent, inclusion, exclusion in zip(parents, inclusions, exclusions):
                self.add_parent(parent)
                parent.add_child(self)
                self.__inclusion_mask.append(inclusion)
                self.__exclusion_mask.append(exclusion)
        def input_signals(self):
            return np.array([parent.value  for parent in self.parents])
        def activation(self):
            return np.sum((self.input_signals() * np.array(self.__inclusion_mask))) > np.sum((self.input_signals() * np.array(self.__exclusion_mask)))

        
    def fit(self,sensory_units:int = 64, association_units:int = 82, response_units:int = 2 ):
        self.__matrix = [[neuron.sensory_unit(0,i,0) for i in range(0,sensory_units)],
                    [neuron.association_unit(1,i,0) for i in range(0,association_units)],
                    [neuron.response_unit(2,i,0) for i in range(0,response_units)]]
        self.__sensory_units = sensory_units
        self.__association_units = association_units
        self.__response_units = response_units
        #for each sensory_units add up to 8 random children (half negative half positive) from the pool of association_units
        excitatory_filter = np.full(int(math.sqrt(association_units)), 1)
        excitatory_filter[:(int(math.sqrt(association_units)/2))] = -1
        for s_unit in self.__matrix[0]:
            np.random.shuffle(excitatory_filter)
            children = np.random.choice(association_units, int(math.sqrt(association_units)),replace=False)
            s_unit.set_children(np.array(self.__matrix[1])[children],excitatory_filter)
        response_connections = np.arange(association_units)
        np.random.shuffle(response_connections)
        response_connections = np.split(response_connections, response_units)
        mutex = np.full(int(association_units / response_units), True)
        mutex[:math.ceil(association_units / (response_units * (response_units * 2)))] = False
        mutex_copy = mutex.copy()
        np.random.shuffle(mutex)
        np.random.shuffle(mutex_copy)
        mutex_list = []
        for a in range(response_units):
            mutex_1 = np.logical_xor(mutex, np.logical_xor(mutex_copy,mutex))
            np.random.shuffle(mutex_copy)
            mutex_2 = np.logical_xor(mutex, np.logical_xor(mutex_copy,mutex))
            np.random.shuffle(mutex_copy)
            mutex_list.append((mutex_1,mutex_2))
        for r_unit, response_connection, mute in zip(self.__matrix[2],response_connections,mutex_list):
            r_unit.set_parents(np.array(self.__matrix[1])[response_connection],mute)
            

        #slice 82 association units into 2 non overlapping subsets 
        #for each of two possible states for each response unit create two overlapping
        

    def sensory_units(self):
        return np.split(np.array([s_unit.value for s_unit in self.__matrix[0]]).T,int(math.sqrt(self.__sensory_units)))

    def set_sensory_units(self, vals: [int]):
        if len(self.__matrix[0]) == len(vals):
            for s_unit, val in zip(self.__matrix[0], vals): s_unit.value = val
            for a_unit in self.__matrix[1]: a_unit.value = sum(a_unit.input_signals())
            for r_unit in self.__matrix[2]: r_unit.value = r_unit.activation()
        else:
            print("Size Mismatch: " + str((len(self.__matrix[0]), len(vals))))

    def association_units(self):
        return np.array([a_unit.value for a_unit in self.__matrix[1]])
    
    def response_units(self):
        return np.array([r_unit.value for r_unit in self.__matrix[2]])
    
