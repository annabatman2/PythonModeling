# -*- coding: utf-8 -*-
"""
Created on 7/4/20
@author: Henry Bishop

Model class: The Model class is used to group a custom function/model written by the user and variables that are used in those functions and perform single calculations
            or sweeps with the custom model.

Most Recent Update 7/4/20
    - Created class

To Do: 
    - Incorporate ability to allow for more than one output from custom function

"""

import numpy as np
from Variable import Variable

class Model():

    def __init__(self, name = "", variables = {}, function = None, functionAttr = ""):
        self.name = name
        self.variables = {}
        self.addVariables(variables)
        self.function = function
        self.functionAttr = functionAttr

    def getName(self):
        return self.name

    def setName(self,name):
        self.name = name

    def getAttr(self):
        return self.functionAttr

    def setAttr(self,attr):
        self.functionAttr = attr

    def addVariables(self, variables):
        #self.variables.update(variables)
        #self.variables.append(variables)
        for var in variables:
            self.variables[var.getName()] = var

    def getVariableNames(self):
        return list(self.variables.keys())

    def runFunction(self):
        return self.function(self.variables)

    def sweepFunction(self, sweepVar):
        array = []
        sweepVar.setSweepVals()
        oldVal = sweepVar.getValue()
        for val in sweepVar.getSweepVals():
            sweepVar.setValue(val)
            array.append(self.runFunction())
        sweepVar.setValue(oldVal)
        return sweepVar.getSweepVals(),array


    