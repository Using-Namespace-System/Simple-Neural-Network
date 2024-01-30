from typing import Any
import numpy as np
import math


class neuron:
    __matrix: [['neuron.unit']]
    __num_sensory_units: int
    __num_association_units: int
    __num_response_units: int
    __sensory_units: ['neuron.sensory_unit']
    __association_units: ['neuron.association_unit']
    __response_units: ['neuron.response_unit']

    class unit(object):

        layer: int
        identifier: int
        value: float
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
        __weight: float
        __signals: [int]
        __min_weight:float 
        threshold: float
        

        @property
        def weight(self):
            return self.__weight
        @weight.setter
        def weight(self, weight):
            if weight<= self.__min_weight:
                self.__weight = self.__min_weight
            else:
                self.__weight = weight


        def __init__(self, *args, threshold:float = 0.569, min_weight:float = 0.02 ):
            super(neuron.association_unit, self).__init__(*args)
            self.threshold = threshold
            self.__excitatory_filter = []
            self.__signals = []
            self.__min_weight = min_weight
            self.weight = 1
        def add_parent(self, *args, filter: int):
            super(neuron.association_unit, self).add_parent(*args)
            self.__excitatory_filter.append(filter)
        def input_signals(self):
            self.__signals = np.array([parent.value * mask for parent,mask in 
                             zip(self.parents, self.__excitatory_filter)])
            return self.__signals
        def activation(self):
            return self.value * self.weight  > self.threshold
        
    class sensory_unit(unit):
        def set_children(self, children: ['neuron.association_unit'], excitatory_filter: [int]):
            for child, filter in zip(children, excitatory_filter):
                child.add_parent(self,filter=filter)
                self.add_child(child)
        
    class response_unit(unit):
        __inclusion_mask: [bool]
        __exclusion_mask: [bool]
        __target: bool
        threshold: float
        @property
        def target(self):
            if self.__target:
                return self.__inclusion_mask
            else:
                return self.__exclusion_mask
        @target.setter
        def target(self, target: int):
            self.__target = bool(target)
            
        def __init__(self, *args, threshold:float = 0.5763):
            super(neuron.response_unit, self).__init__(*args)
            self.__inclusion_mask = []
            self.__exclusion_mask = []
            self.threshold = threshold
        def set_parents(self, parents: ['neuron.association_unit'], inclusions_exclusions: ([bool],[bool])):
            inclusions, exclusions = inclusions_exclusions
            for parent, inclusion, exclusion in zip(parents, inclusions, exclusions):
                self.add_parent(parent)
                parent.add_child(self)
                self.__inclusion_mask.append(inclusion)
                self.__exclusion_mask.append(exclusion)
        def input_signals(self):
            return np.array([parent.activation()  for parent in self.parents])
        def signal_summary(self):
            input_signals = np.array([parent.value  for parent in self.parents])
            masked_signals = (sum(input_signals* np.array(self.__inclusion_mask)), sum(input_signals * np.array(self.__exclusion_mask)))
            masked_activated_signals = (sum(self.input_signals()* np.array(self.__inclusion_mask)), sum(self.input_signals() * np.array(self.__exclusion_mask)))
            return (self.identifier, masked_activated_signals, masked_signals, self.input_signals(), input_signals)

        def activation(self):
            return np.sum((self.input_signals() * np.array(self.__inclusion_mask))) > (np.sum((self.input_signals() * np.array(self.__exclusion_mask)))) + self.threshold
        def reinforce(self,target, *,
                    priority_weight:float = 4,
                    secondary_weight:int = 1,
                    damper:float = 1,
                    offset:float = 0):
            self.target = target
            input_values = np.array([parent.value  for parent in self.parents]) * np.array(self.target)
            secondary_weights = (self.input_signals() * np.array(self.target))
            priority_weights = np.logical_xor(self.__inclusion_mask, self.__exclusion_mask) * np.array(self.target)
            priority_weights = priority_weights * secondary_weights
            #weights = priority_weights + secondary_weights
            weights = priority_weights
            weights = weights * input_values 
            weights = weights * priority_weight
            weights = weights + secondary_weights
            weights = weights * secondary_weight
            weights = weights - (secondary_weight/2)
            weights = weights * damper
            weights = weights + offset
            for parent, weight in zip(self.parents, weights):
                parent.weight =  parent.weight + weight
            
                
        
    def fit(self,sensory_units:int = 64,
            association_units:int = 82,
            response_units:int = 2,
            a_unit_threshold:float = 0.569,
            r_unit_threshold:float = 0.5763,
            a_unit_min_weight:float = 0.02):
        self.__sensory_units = [neuron.sensory_unit(0,i,0) for i in range(0,sensory_units)]
        self.__association_units = [neuron.association_unit(1,i,0, threshold=a_unit_threshold,min_weight=a_unit_min_weight) for i in range(0,association_units)]
        self.__response_units = [neuron.response_unit(2,i,r_unit_threshold) for i in range(0,response_units)]
        self.__num_sensory_units = sensory_units
        self.__num_association_units = association_units
        self.__num_response_units = response_units
        #for each sensory_units add up to 8 random children (half negative half positive) from the pool of association_units
        excitatory_filter = np.full(int(math.sqrt(association_units)), 1)
        excitatory_filter[:(int(math.sqrt(association_units)/2))] = -1
        for s_unit in self.__sensory_units:
            np.random.shuffle(excitatory_filter)
            children = np.random.choice(association_units, int(math.sqrt(association_units)),replace=False)
            s_unit.set_children(np.array(self.__association_units)[children],excitatory_filter)
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
        for r_unit, response_connection, mute in zip(self.__response_units,response_connections,mutex_list):
            r_unit.set_parents(np.array(self.__association_units)[response_connection],mute)
            

        #slice 82 association units into 2 non overlapping subsets 
        #for each of two possible states for each response unit 
        #create two overlapping subsets
        

    def sensory_units(self):
        return np.split(np.array([s_unit.value for s_unit in self.__sensory_units]).T,int(math.sqrt(self.__num_sensory_units)))

    def set_sensory_units(self, vals: [int]):
        if len(self.__sensory_units) == len(vals):
            for s_unit, val in zip(self.__sensory_units, vals): s_unit.value = val
            for a_unit in self.__association_units: a_unit.value = sum(a_unit.input_signals())
            for r_unit in self.__response_units: r_unit.value = r_unit.activation()
        else:
            print("Size Mismatch: " + str((len(self.__sensory_units), len(vals))))

    def association_units(self):
        return np.array([a_unit.value for a_unit in self.__association_units])
    
    def response_units(self):
        return np.array([r_unit.value for r_unit in self.__response_units])
    
    def check_calibration(self,idx, targets):
        results = []
        for r_unit, target in zip(self.__response_units, targets):
            index, activated_mutex, mutex, activated_ingest, ingest = r_unit.signal_summary()
            left, right = mutex
            activated_left, activated_right = activated_mutex
            result = np.array([idx,target,index,activated_left,left,activated_right,right, sum(activated_ingest), sum(ingest)])
            results += [result]
        return results
            
    
    def reinforce(self, targets, **kwargs):
        kwargs = kwargs['kwargs']
        for r_unit, target in zip(self.__response_units, targets ):
            r_unit.reinforce(target, **kwargs)