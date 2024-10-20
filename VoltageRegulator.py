# -*- coding: utf-8 -*-
"""
Created on 6/26/20
@author: Henry Bishop and Katy Flynn

Most Recent Update 7/4/20:
- added setAttr and getAttr
"""

import numpy as np

class VoltageRegulator():
    """ Class that collects Components, Voltage Regulators, and other ComponentGroups
        Attributes:
            - name: (string) name of ComponentGroup
            - VIN: (float) rated input voltage for VoltageRegulator
            - VOUT: (float) rated output voltage for VoltageRegulator
            - Efficiency: (float) single efficiency number for regulator
            - TotalPower: (float) complete power consumption of regulator and load with inefficiency
            - TotalCurrent: (float) complete current consumption of regulator and load with inefficiency
            - RegPower: (float) the regulator's own power consumption
            - RegCurrent: (float) the regulator's own current consumption
            - EffLossPower: (float) power consumption due to inefficiency of regulator
            - EffLossCurrent: (float) current consumption due to inefficiency of regulator
            - LoadPower: (float) power consumption of load
            - LoadCurrent: (float) current consumption of load
            - components: array of Component objects inside of this ComponentGroup
            - componentGroups: array of more ComponentGroups inside of this ComponentGroup
            - voltageRegulators: array of voltageRegulator objects inside of this ComponentGroup
            - hierarchy: once updated, provides tree structure of component-type objects of everything beneath this ComponentGroup
            - Type: (string) "POWER" or "IV", represents that this ComponentGroup is either defined with only power numbers or with voltage/current
        Class Methods:
            PDef() - For defining component in terms of power
            IVDef() - For defining component in terms of voltage/current
        Methods:
            getName() - return string name
            setName() - set new name
            getVIN() - get VIN
            setVIN() - set VIN
            getVOUT() - get VOUT
            setVOUT() - set VOUT
            getEfficiency() - get Efficiency
            setEfficiency() - set Efficiency
            setRegCurrent() - set RegCurrent
            getTotalPower() - returns TotalPower
            getTotalCurrent() - returns TotalCurrent
            getLoadPower() - returns load power
            getLoadCurrent() - returns load current
            setEffLossCurrent() - sets loss current
            setEffLossPower() - sets loss power
            getEffLossCurrent() - gets loss current value
            getEffLossPower() - gets loss power value
            setRegPower() - sets RegPower
            updateTotalPower() - based on Type, go through each section of hierarchy and recalculate TotalPower and possibly TotalCurrent
            checkVDD() - check across hierarchy that VDDs match
            updateLoadPower() - updates load power from across hierarchy
            updateLoadCurrent() - updates load current and power from across hierarchy
            clearHierarchy() - empty hierarchy
            setAttr() - based on string input with same characters as attribute, call the set function for that attribute
            getAttr() - based on string input with same characters as attribute, call the get function for that attribute
    """
    
    def __init__(self, name = None, VIN = None, VOUT = None, Efficiency = 1.0, RegPower = 0.0, RegCurrent = None, components = np.array([]), componentGroups = np.array([]), voltageRegulators = np.array([])):
        self.name = name
        self.VIN = VIN
        self.VOUT = VOUT
        self.Efficiency = Efficiency
        self.TotalPower = 0.0       # EVERYTHING
        self.TotalCurrent = None
        self.InactivePower = 0.0
        self.InactiveCurrent = None
        self.RegPower = RegPower    # Power due to quiescent regulator current
        self.RegCurrent = RegCurrent
        self.EffLossPower = 0.0     # Power due to voltage drop
        self.EffLossCurrent = None
        self.LoadPower = 0.0
        self.LoadCurrent = None
        self.InactiveLoadPower = 0.0
        self.InactiveLoadCurrent = None
        self.components = components
        self.componentGroups = componentGroups
        self.voltageRegulators = voltageRegulators
        self.hierarchy = dict(comp=components,compGroups=componentGroups,vReg=voltageRegulators) # hierarchy is EVERYTHING and is CALCULATED, original inputs are just one level
        self.Type = None

    @classmethod
    def PDef(cls, name, Efficiency, RegPower, components, componentGroups, voltageRegulators):
        newVReg = VoltageRegulator(name = name, Efficiency = Efficiency, RegPower = RegPower, components = components, componentGroups = componentGroups, voltageRegulators = voltageRegulators)
        newVReg.Type = "POWER"
        newVReg.updateTotalPower()
        return newVReg

    @classmethod
    def IVDef(cls, name, VIN, VOUT, Efficiency, RegCurrent, components, componentGroups, voltageRegulators):
        newVReg = VoltageRegulator(name = name, VIN = VIN, VOUT = VOUT, Efficiency = Efficiency, RegCurrent = RegCurrent, components = components, componentGroups = componentGroups, voltageRegulators = voltageRegulators)
        newVReg.Type = "IV"
        newVReg.updateTotalPower()
        return newVReg

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getVIN(self):
        return self.VIN

    def setVIN(self,newVIN):
        if(newVIN < 0):
            print(newVIN, " is less than zero - no update.")
            return
        self.VIN = newVIN

    def getVOUT(self):
        return self.VOUT

    def setVOUT(self,newVOUT):
        if(newVOUT < 0):
            print(newVOUT, " is less than zero - no update.")
            return
        self.VOUT = newVOUT

    def getEfficiency(self):
        return self.Efficiency

    def setEfficiency(self, newEff):
        self.Efficiency = newEff

    def setRegCurrent(self, newRegCurrent):
        if(newRegCurrent < 0):
            print(newRegCurrent, " is less than zero - no update.")
            return
        self.RegCurrent = newRegCurrent

    def getTotalPower(self):
        return self.TotalPower

    def getTotalCurrent(self):
        return self.TotalCurrent

    def getInactivePower(self):
        return self.InactivePower

    def getInactiveCurrent(self):
        return self.InactiveCurrent

    def getLoadPower(self):
        return self.LoadPower

    def getLoadCurrent(self):
        return self.LoadCurrent

    def setEffLossCurrent(self):
        self.EffLossCurrent = self.LoadCurrent / self.Efficiency - self.LoadCurrent

    def setEffLossInactiveCurrent(self):
        self.EffLossInactiveCurrent = self.InactiveLoadCurrent / self.Efficiency - self.InactiveLoadCurrent

    def setEffLossPower(self):
        self.EffLossPower = self.LoadPower / self.Efficiency - self.LoadPower

    def setEffLossInactivePower(self):
        self.EffLossInactivePower = self.InactiveLoadPower / self.Efficiency - self.InactiveLoadPower

    def getEffLossCurrent(self):
        return self.EffLossCurrent
    
    def getEffLossPower(self):
        return self.EffLossPower

    def setRegPower(self,newRegPower):
        self.RegPower = newRegPower

    def updateTotalPower(self):
        self.updateInactivePower()
        if self.Type == "POWER":
            self.updateLoadPower()
            self.setEffLossPower()
            self.TotalPower = self.RegPower + self.LoadPower / self.Efficiency
        elif self.Type == "IV":
            self.updateLoadCurrent()
            self.setEffLossCurrent()
            self.setEffLossPower()
            self.RegPower = self.VIN * self.RegCurrent
            self.TotalPower = self.RegCurrent * self.VIN + self.LoadCurrent * self.VOUT / self.Efficiency
            self.TotalCurrent = self.TotalPower / self.VIN
        else:
            print("VoltageRegulator didn't have correct Type - no update. (updateTotalPower)")

    def updateInactivePower(self):
        if self.Type == "POWER":
            self.updateInactiveLoadPower()
            self.setEffLossInactivePower()
            self.InactivePower = self.RegPower + self.InactiveLoadPower / self.Efficiency
        elif self.Type == "IV":
            self.updateInactiveLoadCurrent()
            self.setEffLossInactiveCurrent()
            self.setEffLossInactivePower()
            self.RegPower = self.VIN * self.RegCurrent
            self.InactivePower = self.RegCurrent * self.VIN + self.InactiveLoadCurrent * self.VOUT / self.Efficiency
            self.InactiveCurrent = self.InactivePower / self.VIN
        else:
            print("VoltageRegulator didn't have correct Type - no update. (updateInactivePower)")

    def checkVDD(self):
        for comp in self.hierarchy["comp"]:
            if (comp.getVDD() != self.VOUT):
                print("Component", comp.name,"VDD,", comp.getVDD(),", doesn't match", self.name, "VOUT,", self.VOUT)
                assert (False)
        for comp in self.hierarchy["compGroups"]:
            if (comp.getVDD() != self.VOUT):
                print("Component Group", comp.name,"VDD,", comp.getVDD(),", doesn't match", self.name, "VOUT", self.VOUT)
                assert (False)
        for comp in self.hierarchy["vReg"]:
            if (comp.getVIN() != self.VOUT):
                print("Regulator", comp.name,"VIN,", comp.getVIN(),", doesn't match", self.name, "VOUT", self.VOUT)
                assert (False)

    def updateLoadPower(self):
        tempSum = 0.0
        for comp in self.components:
            tempSum = tempSum + comp.getTotalPower()
        for comp in self.componentGroups:
            tempSum = tempSum + comp.getTotalPower()
        for comp in self.voltageRegulators:
            tempSum = tempSum + comp.getTotalPower()
        self.LoadPower = tempSum

    def updateInactiveLoadPower(self):
        tempSum = 0.0
        for comp in self.components:
            tempSum = tempSum + comp.getInactivePower()
        for comp in self.componentGroups:
            tempSum = tempSum + comp.getInactivePower()
        for comp in self.voltageRegulators:
            tempSum = tempSum + comp.getInactivePower()
        self.InactiveLoadPower = tempSum

    def updateLoadCurrent(self):
        tempSum = 0.0
        self.checkVDD()
        for comp in self.components:
            tempSum = tempSum + comp.getTotalPower()
        for comp in self.componentGroups:
            tempSum = tempSum + comp.getTotalPower()
        for comp in self.voltageRegulators:
            tempSum = tempSum + comp.getTotalPower()
        self.LoadCurrent = tempSum / self.VOUT
        self.LoadPower = tempSum

    def updateInactiveLoadCurrent(self):
        tempSum = 0.0
        self.checkVDD()
        for comp in self.components:
            tempSum = tempSum + comp.getInactivePower()
        for comp in self.componentGroups:
            tempSum = tempSum + comp.getInactivePower()
        for comp in self.voltageRegulators:
            tempSum = tempSum + comp.getInactivePower()
        self.InactiveLoadCurrent = tempSum / self.VOUT
        self.InactiveLoadPower = tempSum

    def clearHierarchy(self):
        self.hierarchy = dict(comp=np.array([]),compGroups=np.array([]),vReg=np.array([]))

    def setAttr(self, attrKey, value):
        attrDict = {    # Dictionary of attributes meant for sweeping
            #"VIN":self.setVIN,
            #"VOUT":self.setVOUT,
            "Efficiency":self.setEfficiency,
            "RegPower":self.setRegPower,
            "RegCurrent":self.setRegCurrent
        }    
        attrDict[attrKey](value)

    def getAttr(self, attrKey):
        attrDict = {    # Dictionary of attributes meant for sweeping
            "TotalPower":self.getTotalPower,
            "TotalCurrent":self.getTotalCurrent,
            "LoadPower":self.getLoadPower,
            "LoadCurrent":self.getLoadCurrent
        }    
        return attrDict[attrKey]()