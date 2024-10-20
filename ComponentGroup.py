# -*- coding: utf-8 -*-
"""
Created on 6/26/20
@author: Henry Bishop and Katy Flynn

"""
import numpy as np

class ComponentGroup:
    """ Class that collects Components, Voltage Regulators, and other ComponentGroups
        Attributes:
            - name: (string) name of ComponentGroup
            - VDD: (float) rated voltage for ComponentGroup
            - components: array of Component objects inside of this ComponentGroup
            - componentGroups: array of more ComponentGroups inside of this ComponentGroup
            - voltageRegulators: array of voltageRegulator objects inside of this ComponentGroup
            - hierarchy: once updated, provides tree structure of component-type objects of everything beneath this ComponentGroup
            - TotalPower: (float) once updated, summation of all average power of component-type objects beneath this ComponentGroup
            - TotalCurrent: (float) once updated, summation of all average current of component-type objects beneath this ComponentGroup
            - Type: (string) "POWER" or "IV", represents that this ComponentGroup is either defined with only power numbers or with voltage/current
            - InactivePower: (float) once updated, summation of floor power for ComponentGroup
            - InactiveCurrent: (float) once updated, summation for floor current for ComponentGroup
        Class Methods:
            PDef() - For defining component in terms of power
            IVDef() - For defining component in terms of voltage/current
        Methods:
            getTotalPower() - return TotalPower value
            getInactivePower() - return InactivePower value
            updateTotalPower() - based on Type, go through each section of hierarchy and recalculate TotalPower and possibly TotalCurrent
            updateInactivePower() - based on Type, go through each section of hierarchy and recalculate InactivePower and possibly InactiveCurrent
            addComponents() - add new Component to Components section in hierarchy
            addComponentGroups() - add new ComponentGroups to ComponentGroups section in hierarchy
            addVoltageRegulators() - add new VoltageRegulator to VotlageRegulators section hin hierarchy
            getName() - return string name
            setName() - set new name
            setVDD() - set VDD
            getVDD() - return VDD
            checkVDD() - check across hierarchy that VDDs match
            clearHierarchy() - empty hierarchy
    """
    
    def __init__(self, name = None, VDD = None, components = np.array([]), componentGroups = np.array([]), voltageRegulators = np.array([]), checkVDDFlag = True):
        """ __init__ - set the voltage for all components
            Compute the various power points as function of the components
            Update the currents for the VDD
            Initialize base class parameters
        """
        self.name = name
        self.VDD = VDD 
        self.components = np.array(components)
        self.componentGroups = np.array(componentGroups)
        self.voltageRegulators = np.array(voltageRegulators)
        self.hierarchy = dict(comp=components,compGroups=componentGroups,vReg=voltageRegulators) # hierarchy is EVERYTHING and is CALCULATED, original inputs are just one level
        self.TotalPower = 0.0
        self.TotalCurrent = None
        self.InactivePower = 0.0
        self.InactiveCurrent = None
        self.Type = None
        self.checkVDDFlag = checkVDDFlag

    @classmethod
    def PDef(cls, name, components, componentGroups, voltageRegulators, checkVDDFlag = True):
        newComponentGroup = cls(name = name, components = components, componentGroups = componentGroups, voltageRegulators = voltageRegulators, checkVDDFlag = checkVDDFlag)
        newComponentGroup.Type = "POWER"
        newComponentGroup.updateTotalPower()
        return newComponentGroup

    @classmethod
    def IVDef(cls, name, VDD, components, componentGroups, voltageRegulators, checkVDDFlag = True):
        newComponentGroup = cls(name = name, VDD = VDD, components = components, componentGroups = componentGroups, voltageRegulators = voltageRegulators, checkVDDFlag = checkVDDFlag)
        newComponentGroup.Type = "IV"
        newComponentGroup.updateTotalPower()
        return newComponentGroup

    def getTotalPower(self):
        return self.TotalPower

    def getInactivePower(self):
        return self.InactivePower

    def updateTotalPower(self):
        self.updateInactivePower()
        if self.Type == "POWER":
            tempSum = 0.0
            for comp in self.hierarchy["comp"]:
                tempSum = tempSum + comp.getTotalPower()
            for comp in self.hierarchy["compGroups"]:
                tempSum = tempSum + comp.getTotalPower()
            for comp in self.hierarchy["vReg"]:
                tempSum = tempSum + comp.getTotalPower()
            self.TotalPower = tempSum
        elif self.Type == "IV":
            self.checkVDD()
            tempSum = 0.0
            for comp in self.hierarchy["comp"]:
                tempSum = tempSum + comp.getTotalPower()
            for comp in self.hierarchy["compGroups"]:
                tempSum = tempSum + comp.getTotalPower()
            for comp in self.hierarchy["vReg"]:
                tempSum = tempSum + comp.getTotalPower()
            self.TotalPower = tempSum
            self.TotalCurrent = self.TotalPower / self.VDD

    def updateInactivePower(self):
        if self.Type == "POWER":
            tempSum = 0.0
            for comp in self.hierarchy["comp"]:
                tempSum = tempSum + comp.getInactivePower()
            for comp in self.hierarchy["compGroups"]:
                tempSum = tempSum + comp.getInactivePower()
            for comp in self.hierarchy["vReg"]:
                tempSum = tempSum + comp.getInactivePower()
            self.InactivePower = tempSum
        elif self.Type == "IV":
            self.checkVDD()
            tempSum = 0.0
            for comp in self.hierarchy["comp"]:
                tempSum = tempSum + comp.getInactivePower()
            for comp in self.hierarchy["compGroups"]:
                tempSum = tempSum + comp.getInactivePower()
            for comp in self.hierarchy["vReg"]:
                tempSum = tempSum + comp.getInactivePower()
            self.InactivePower = tempSum
            self.InactiveCurrent = self.InactivePower / self.VDD

    def addComponents(self, newComps):
        np.append(self.hierarchy["comp"],newComps)

    def addComponentGroups(self, newGroups):
        np.append(self.hierarchy["compGroups"],newGroups)

    def addVoltageRegulators(self, newVRegs):
        np.append(self.hierarchy["vReg"],newVRegs)

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def setVDD(self, newVDD):
        self.VDD = newVDD

    def getVDD(self):
        return self.VDD
    
    def checkVDD(self):
        if(self.checkVDDFlag):
            for comp in self.hierarchy["comp"]:
                if (comp.getVDD() != self.VDD):
                    print("Component", comp.name,"VDD,", comp.getVDD(),", doesn't match", self.name, "VDD,", self.VDD)
                    assert (False)
            for comp in self.hierarchy["compGroups"]:
                if (comp.getVDD() != self.VDD):
                    print("Component Group", comp.name,"VDD,", comp.getVDD(),", doesn't match", self.name, "VDD", self.VDD)
                    assert (False)
            for comp in self.hierarchy["vReg"]:
                if (comp.getVIN() != self.VDD):
                    print("Regulator", comp.name,"VIN,", comp.getVIN(),", doesn't match", self.name, "VDD", self.VDD)
                    assert (False)

    def clearHierarchy(self):
        self.hierarchy = dict(comp=np.array([]),compGroups=np.array([]),vReg=np.array([]))