# -*- coding: utf-8 -*-
"""
Created on 7/4/20
@author: Henry Bishop

Variable class: Used to define a "variable" in a custom equation-based model based on the Model class.
                An instance of the Variable class allows for static and swept values to be a part of its
                definition.

Most Recent Update 7/4/20
    - Created class

"""

import numpy as np

class Variable():

    def __init__(self, name = "", value = 0, start = None, stop = None, step = None, unit = None):
        self.name = name
        self.value = value
        self.start = start
        self.stop = stop
        self.step = step
        self.sweepVals = None
        self.unit = unit    # String representation of applicable unit
        self.sweepValSize = 0   
        if(start != None and stop != None and step != None):
            self.setSweepVals()

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getUnit(self):
        return self.unit

    def setUnit(self, unit):
        self.unit = unit

    def getStart(self):
        return self.start

    def getStop(self):
        return self.stop

    def getStep(self):
        return self.step

    def setSweepVals(self):
        temp = np.arange(self.getStart(),self.getStop(),self.getStep(),float)
        self.sweepVals = temp.tolist()
        self.sweepValSize = len(self.sweepVals)

    def getSweepVals(self):
        return self.sweepVals

    def getValue(self):
        return self.value

    def setValue(self, val):
        self.value = val

    def getSweepSize(self):
        return self.sweepValSize