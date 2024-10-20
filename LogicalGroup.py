# -*- coding: utf-8 -*-
"""
Created on 11/18/20
@author: Henry Bishop

Most Recent Update 11/18/20:
- Created LogicalGroup class
"""
import numpy as np

class LogicalGroup:

    """
    LogicalGroup:
    This class is meant to collect components/componentGroups/voltageRegulators not based on hierarchy but based on association.
    For example, if I have many components in a system that collectively represent the analog front end, but run on various different
    voltage rails, then the LogicalGroup can collect all those parts to represent the total power for the AFE. It is a reduced version
    of the ComponentGroup class.

    Attributes:
        - name: (string) name of ComponentGroup
        - components: array of Component objects inside of this ComponentGroup
        - componentGroups: array of more ComponentGroups inside of this ComponentGroup
        - voltageRegulators: array of voltageRegulator objects inside of this ComponentGroup
        - hierarchy: once updated, provides tree structure of component-type objects of everything beneath this ComponentGroup
        - TotalPower: (float) once updated, summation of all average power of component-type objects beneath this ComponentGroup
    Methods:
        getTotalPower() - return TotalPower value
        clearHierarchy() - 

    """

    def __init__(self, name = None, components = np.array([]), componentGroups = np.array([]), voltageRegulators = np.array([])):
        self.name = name
        self.components = np.array(components)
        self.componentGroups = np.array(componentGroups)
        self.voltageRegulators = np.array(voltageRegulators)
        self.hierarchy = dict(comp=components,compGroups=componentGroups,vReg=voltageRegulators)
        self.TotalPower = 0.0
        self.InactivePower = 0.0
        self.updateTotalPower()
        self.getTotalPower()

    def setName(self,name):
        self.name = name

    def getTotalPower(self):
        return self.TotalPower

    def getInactivePower(self):
        return self.InactivePower

    def getName(self):
        return self.name

    def updateTotalPower(self):
        self.updateInactivePower()
        tempSum = 0.0
        for comp in self.hierarchy["comp"]:
            tempSum = tempSum + comp.getTotalPower()
        for comp in self.hierarchy["compGroups"]:
            tempSum = tempSum + comp.getTotalPower()
        for comp in self.hierarchy["vReg"]:
            tempSum = tempSum + comp.getTotalPower()
        self.TotalPower = tempSum

    def updateInactivePower(self):
        tempSum = 0.0
        for comp in self.hierarchy["comp"]:
            tempSum = tempSum + comp.getInactivePower()
        for comp in self.hierarchy["compGroups"]:
            tempSum = tempSum + comp.getInactivePower()
        for comp in self.hierarchy["vReg"]:
            tempSum = tempSum + comp.getInactivePower()
        self.InactivePower = tempSum

    def clearHierarchy(self):
        self.hierarchy = dict(comp=np.array([]),compGroups=np.array([]),vReg=np.array([]))


