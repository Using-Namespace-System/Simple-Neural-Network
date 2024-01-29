import numpy as np
import sys

this = sys.modules[__name__]

this.__model = None
this.__targets = {}

def import_model(model):
    this.__model = model

@property
def target(input):
    if this.__targets[input]:
        return this.__targets[input]
    else:
        return input
def map_targets(map):
    this.__targets = {key: value for key, value in map}


def fit():
    this.__model.fit()

def predictions(training_set):
    results = []
    for percept in training_set:
        this.__model.set_sensory_units(percept.flatten())
        results += [binary_decode(this.__model.response_units())]
    return results

def binary_decode(bytearray: [int]):
    return sum(bytearray * (2 ** np.array(list(enumerate(bytearray.flat)))[:,0]))

def binary_encode(ingest: [int], meta: [int]):
    return np.floor_divide(ingest, (2 ** np.array(list(enumerate(meta)))[:,0])) % 2


def representation(results, targets):
    results = [[percept, target] for percept, target in zip(results,targets)]

    result = np.unique(results, axis = 0, return_counts= True)
    target = np.unique(np.array(results).T[1], axis = 0, return_counts= True)
    goal = [target[1][r] for r in result[0][:,1]]
    accuracy = np.array([result[0][:,0],result[0][:,1],result[1]/goal]).T

    accuracy = accuracy[accuracy[:, 1].argsort()]
    targets = np.unique(accuracy[:,1].astype(int), return_index=True)
    representation = np.split(accuracy, targets[1][1:])

    results = []
    for rep in representation:
        rep = rep[(-rep[:,2]).argsort()][0,:]
        results += [rep]
        #this.__targets[rep[1]] = rep[0]

    return np.array(results)
    


def accuracy(results, targets):
    results = [[percept, target] for percept, target in zip(results,targets)]

    result = np.unique(results, axis = 0, return_counts= True)
    target = np.unique(np.array(results).T[1], axis = 0, return_counts= True)
    summed = {summed[0]: summed[1] for summed in np.array(target).T}
    goal = [summed[r] for r in result[0][:,1]]

    return np.array([result[0][:,0],result[0][:,1],result[1]/goal]).T

def reinforce(training_set, targets):
    results = []
    for percept, target in zip(training_set, targets):
        this.__model.set_sensory_units(percept.flatten())
        this.__model.reinforce(binary_encode(target, this.__model.response_units()))
        this.__model.set_sensory_units(percept.flatten())
        results += [binary_decode(this.__model.response_units())]
    return results

def check_calibration(training_set, targets):
    results = []
    index = enumerate(targets)
    index = np.array(list(index))[:,0]
    for idx, percept, target in zip(index, training_set, targets):
        this.__model.set_sensory_units(percept.flatten())
        result = np.array(this.__model.check_calibration(idx,binary_encode(target, this.__model.response_units())))
        for r in result:
            results += [r]
        
    return results