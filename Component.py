# -*- coding: utf-8 -*-
"""
Created on 6/26/20
@author: Henry Bishop and Katy Flynn

Most Recent Update 7/4/20:
- added setAttr and getAttr

** Mode-related capability is legacy
"""
# from ComponentMode import ComponentMode
from Variable import Variable

class Component:
    """ base class for leaf components in a hierarchical component definition
        Attributes:
            name: (string) name of the component
            ActivePower: (float) the power of the component at a duty cycle of 1.0
            InactivePower: (float) the power of the component at a duty cycle of 0.0
            ActiveCurrent: (float) the power of the component at a duty cycle of 1.0 (optional)
            InactiveCurrent: (float) the power of the component at a duty cycle of 0.0 (optional)
            VDD: (float) rated voltage of the component (optional)
            DutyCycle: (float in range [0.0, 1.0]) the duty cycle of the component
            TotalPower: (float) the average power at the current duty cycle
            TotalCurrent: (float) the average current at the current duty cycle
            Type: (string) either "POWER" or "IV" to denote if Component is defined with only Power or Voltage/Current
            Modes: (dict) a dictionary of ComponentModes (and children) in which the component can operate
            CurrentModeName: (string) the name of the current mode
        Class Methods:
            PDef() - For defining component in terms of power
            IVDef() - For defining component in terms of voltage/current
        Methods:
            updateTotalPower() - recomputes the total power
            displayName() - prints name of component
            displayOperatingPoint() - prints readable power-related info about component
            convertCurrentToPower() - recalculates all power values based on voltage and currents
            _computeTotalPower() - internal method for calculating total power

            getName()
            getInactiveCurrent()
            getActiveCurrent()
            getVDD()
            getDutyCycle()
            getInactivePower()
            getActivePower()
            getTotalPower()
            getPowerOverDutyCycleRange(DutyCycleRange) - returns list of TotalPowers associated with input list of different duty cycles

            setName()
            setInactiveCurrent()
            setActiveCurrent()
            setVDD()
            setDutyCycle()
            setInactivePower()
            setActivePower()
            setTotalPower() - assigns new DutyCycle to component based on active/inactive and new total power input

            setAttr() - based on string input with same characters as attribute, call the set function for that attribute
            getAttr() - based on string input with same characters as attribute, call the get function for that attribute
    """
        
    def __init__(self, name = None, ActivePower = 0.0, InactivePower = 0.0, ActiveCurrent = None, InactiveCurrent = None, VDD = None, DutyCycle = 0.0, Models = []):
        self.name = name
        self.ActivePower = ActivePower
        self.InactivePower = InactivePower
        self.ActiveCurrent = ActiveCurrent
        self.InactiveCurrent = InactiveCurrent
        self.VDD = VDD
        self.DutyCycle = DutyCycle
        self.TotalPower = 0.0
        self.TotalCurrent = 0.0
        self.Type = None
        self.Models = {}
        self.CurrentModel = None
        self.CurrentModelVal = None
        self.addModels(Models)

    @classmethod
    def PDef(cls, name, ActivePower, InactivePower, DutyCycle, Models = []):
        newComponent = cls(name = name, ActivePower = ActivePower, InactivePower = InactivePower, DutyCycle = DutyCycle, Models = Models)
        newComponent.Type = "POWER"
        newComponent.updateTotalPower(verbose=True)
        return newComponent

    @classmethod
    def IVDef(cls, name, ActiveCurrent, InactiveCurrent, VDD, DutyCycle, Models = []):
        newComponent = cls(name = name, ActiveCurrent = ActiveCurrent, InactiveCurrent = InactiveCurrent, VDD = VDD, DutyCycle = DutyCycle, Models = Models)
        newComponent.Type = "IV"
        newComponent.updateTotalPower(verbose=True)
        return newComponent
        
    def displayName( self ):
        print( "Name : ", self.name )
        
    def displayOperatingPoint( self ):
        """ displayOperatingPoint - output the operating condition for the Component instance
        """
        print( self.name, " has Total Power:(", self.TotalPower,") at Duty Cycle (", self.DutyCycle,"), with Sleep Power (", self.InactivePower,") and Peak Power (", self.ActivePower,")")        
  
    def getName(self):
        return self.name

    def getActivePower(self):
        return self.ActivePower

    def getInactivePower(self):
        return self.InactivePower

    def getActiveCurrent(self):
        return self.ActiveCurrent

    def getInactiveCurrent(self):
        return self.InactiveCurrent

    def getVDD(self):
        return self.VDD

    def getDutyCycle( self ):
        return self.DutyCycle

    def getTotalPower(self):
        return self.TotalPower

    def getTotalCurrent(self):
        return self.TotalCurrent

    def setName(self, newName):
        self.name = newName

    def setActivePower( self, NewActivePower ):
        """ setActivePower - update the ActivePower to a positive value greater than the InactivePower
            update the TotalPower accordingly
        """
        if ( NewActivePower < 0 ):
            print( NewActivePower, " is less than 0 - no update.")
        elif ( NewActivePower < self.InactivePower ):
            print( NewActivePower, " is less than the sleep power (", self.InactivePower, ") - no update.")
            return
        self.ActivePower = NewActivePower
        #self.updateTotalPower() 

    def setInactivePower( self, NewInactivePower ):
        """ setInactivePower - update the InactivePower to a positive value
            update the TotalPower accordingly
        """
        if ( NewInactivePower < 0 ):
            print( NewInactivePower, " is less than 0 - no update.")
            return
        self.InactivePower = NewInactivePower
        #self.updateTotalPower()

    def setActiveCurrent(self, newActiveCurrent):
        """ setActiveCurrent - update the ActiveCurrent to a positive value
            update the TotalCurrent/TotalPower accordingly
        """
        if ( newActiveCurrent < 0 ):
            print(newActiveCurrent, " is less than 0 - no update.")
            return
        self.ActiveCurrent = newActiveCurrent
        #self.updateTotalPower()

    def setInactiveCurrent(self, newInactiveCurrent):
        """ setInactiveCurrent - update the InactiveCurrent to a positive value
            update the TotalCurrent/TotalPower accordingly
        """
        if ( newInactiveCurrent < 0 ):
            print(newInactiveCurrent, " is less than 0 - no update.")
            return
        self.ActiveCurrent = newInactiveCurrent
        #self.updateTotalPower()

    def setVDD(self, newVDD):
        if newVDD < 0:
            print(newVDD, " is less than 0 - no update.")
            return
        self.VDD = newVDD
        #self.updateTotalPower()

    def setDutyCycle(self, newDutyCycle):
        if(newDutyCycle > 1 or newDutyCycle < 0):
            print(newDutyCycle, " is out of allowable bounds between 0 and 1.")
            return
        self.DutyCycle = newDutyCycle
        #self.updateTotalPower()

    def updateTotalPower(self, verbose = False):
        """
        updateTotalPower: Depending on if the model should replace the duty cycle model or not, update total power
        """
        if (self.CurrentModel == None):
            if self.Type == "POWER":
                if verbose: print("Updating TotalPower with power type and without external model for component:",self.getName())
                self.TotalPower = self.InactivePower + (self.ActivePower - self.InactivePower) * self.DutyCycle
            elif self.Type == "IV":
                if verbose: print("Updating TotalPower with IV type and without external model for component:",self.getName())
                self.TotalCurrent = self.InactiveCurrent + (self.ActiveCurrent - self.InactiveCurrent) * self.DutyCycle
                self.ActivePower = self.ActiveCurrent * self.VDD
                self.InactivePower = self.InactiveCurrent * self.VDD
                self.TotalPower = self.VDD * self.TotalCurrent                
        else:
            if self.Type == "POWER":
                if(self.CurrentModel.getAttr() == "TotalPower"):
                    if verbose: print("Updating TotalPower with power type, with external model assigning to TotalPower for component:",self.getName())
                    self.runModel()
                else:
                    if verbose: print("Updating TotalPower with power type, with external model assigning to Inactive/Active Power or DutyCycle for component:",self.getName())
                    self.runModel()
                    self.TotalPower = self.InactivePower + (self.ActivePower - self.InactivePower) * self.DutyCycle
            elif self.Type == "IV":
                if(self.CurrentModel.getAttr() == "TotalCurrent"):
                    if verbose: print("Updating TotalPower with IV type, with external model assigning to TotalCurrent for component:",self.getName())
                    self.runModel()
                else:
                    if verbose: print("Updating TotalPower with IV type, with external model assigning to Inactive/Active Current or DutyCycle for component:",self.getName())
                    self.runModel()
                    self.TotalCurrent = self.InactiveCurrent + (self.ActiveCurrent - self.InactiveCurrent) * self.DutyCycle
                    self.ActivePower = self.ActiveCurrent * self.VDD
                    self.InactivePower = self.InactiveCurrent * self.VDD
                    self.TotalPower = self.VDD * self.TotalCurrent

    def setTotalPower(self,Total):
        if self.Type == "POWER":
            self.TotalPower = Total
        elif self.Type == "IV":
            self.TotalCurrent = Total
            self.TotalPower = self.TotalCurrent * self.VDD

    def setAttr(self, attrKey, value):
        if(self.Type == "POWER"):
            attrDict = {    # Dictionary of attributes meant for sweeping
                "TotalPower":self.setTotalPower,
                "ActivePower":self.setActivePower,
                "InactivePower":self.setInactivePower,
                "DutyCycle":self.setDutyCycle
            }    
            if(attrKey in attrDict):
                attrDict[attrKey](value)
            else:
                print("Component class: AttrKey not valid")
        elif(self.Type == "IV"):
            attrDict = {    # Dictionary of attributes meant for sweeping
                "TotalCurrent":self.setTotalPower,  # Actually sets TotalCurrent
                "ActiveCurrent":self.setActiveCurrent,
                "InactiveCurrent":self.setInactiveCurrent,
                "VDD":self.setVDD,
                "DutyCycle":self.setDutyCycle
            }    
            if(attrKey in attrDict):
                attrDict[attrKey](value)
            else:
                print("Component class: AttrKey not valid")

    def getAttr(self, attrKey):
        attrDict = {    # Dictionary of attributes meant for sweeping
            "TotalPower":self.getTotalPower,
            "TotalCurrent":self.getTotalCurrent
        }    
        return attrDict[attrKey]()

    def setCurrentModel(self, modelName):
        self.CurrentModel = self.Models[modelName]
        self.updateTotalPower(verbose=True)

    def addModels(self,modelList):
        if(len(modelList) > 0):
            for model in modelList:
                self.Models[model.getName()] = model
    
    def removeModels(self,modelNames):
        for name in modelNames:
            self.Models.pop(name)

    def hasCurrentModel(self):
        if(self.CurrentModel == None): return False
        else: return True

    def getCurrentModelName(self):
        return self.CurrentModel.getName()

    def runModel(self): # Will run the model once and assign the value to the component attribute
        if(self.CurrentModel != None):
            self.CurrentModelVal = self.CurrentModel.runFunction()
            self.setAttr(self.CurrentModel.getAttr(),self.CurrentModelVal)
            #return self.CurrentModelVal, self.TotalPower
        else:
            print("runModel failed: no model assigned")

# #######TEST#######
# #m1 = Component(RX,10.0,0.0,None,None,None, .5)
# voltage = 2.0
# active_current = 3.0
# inactive_current = 1.0
# duty_cycle = 0.1
# name = "test"
# # active_power = 4.0
# # inactive_power = .1

# m1 = Component.IVDef(name, active_current, inactive_current, voltage, duty_cycle)
# print(m1.getActiveCurrent())
# print(m1.getInactiveCurrent())
# print(m1.getTotalPower())
# print(m1.getVDD())
# print(m1.getDutyCycle())
# print(m1.getName()) 
# m1.setDutyCycle(0.2)
# print(m1.getTotalPower())

# m1.setter("ActiveCurrent",4.0)
# print(m1.getActiveCurrent())
# print(m1.getTotalPower())


# m2 = Component.PDef(name, active_power, inactive_power, duty_cycle)
# print(m2.getTotalPower())
# print(m2.getName()) 
# print(m2.getVDD())
# print(m2.getDutyCycle())
# print(m2.getInactiveCurrent())
# print(m2.getActiveCurrent())
# print(m2.__dict__)