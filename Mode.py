# -*- coding: utf-8 -*-
"""
Created on 3/12/21
@author: Henry Bishop

"""
from Model import Model
from Component import Component
import ComponentFunctions as CF

class Mode:
    """
    Mode Class: The mode class represents the collection of components and models which allows for a system to be reset
                to different operating points with a simple function call. This allows for further abstraction and simplification
                of system operation. Modes can be "averaged" together as well.
    Atrributes:
        - name: (string) name of the particular mode
        - components: list of components and associated models needed to generate a whole system mode
        - modelName: list of string names of the models already assigned to a given component which should be used in this Mode
        - system: the system component-like object in question
        - TotalPower: the last calculated total power for the system in this mode
        - dutyFactor: the associated duty factor for this mode in the system (optional)
        - modes: list of modes for a particular system

    """

    def __init__(self, name = "", components = [], modelNames = [], system = None, dutyFactor = 0, modes = []):
        self.name = name
        self.components = components
        self.modelNames = modelNames
        self.system = system
        self.dutyFactor = dutyFactor
        self.modes = modes
        self.TotalPower = 0
        self.AverageModePower = None
        self.useMode()

    def useMode(self):
        '''
        useMode: updates the entire system's operating point based on the desired mode
        '''
        for i in range(len(self.components)):
            self.components[i].setCurrentModel(self.modelNames[i])
        CF.updateHierarchy(self.system)
        self.TotalPower = self.system.getTotalPower()
        print("Mode",self.name,"applied to",self.system.getName(),".")
        print("Mode power is",self.TotalPower)
        return self.TotalPower

    def averageModes(self):
        '''
        averageModes: takes an arbitrary number of operating modes and their associated duty factors to calculate an average power
        '''
        tempPower = 0
        for mode in self.modes:
            tempPower += mode.useMode()
        self.AverageModePower = tempPower/len(self.modes)
        return self.AverageModePower

    def setName(self,name):
        self.name = name

    def getName(self):
        return self.name

    def getTotalPower(self):
        return self.TotalPower
        