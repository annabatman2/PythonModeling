# -*- coding: utf-8 -*-
"""
Created on 3/4/21
@author: Ben Calhoun


"""
from Component import Component
from ComponentGroup import ComponentGroup
from LogicalGroup import LogicalGroup
from VoltageRegulator import VoltageRegulator
from Variable import Variable
from Model import Model
import ComponentFunctions as CF
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Notes about model quirks
# - active power shouldn't be listed as zero, it should be at least the leakage power if not listed, meaning that there is no active component it just stays at leakage level

# voltage rails
VddIO = 1.2
Vdd1 = 1.0
Vdd2 = 0.5

# A generic variable and function to represent duty-cycle
DC = Variable("Duty_Cycle",1,0.0001,1,0.0001)

# set up duty cycle sweeps

def DutyCycle(varDictionary):
    dutycycle = varDictionary["Duty_Cycle"].value
    return dutycycle

# Creating several Models objects to represent AFE and TX duty-cycle
afeDutyCycleModelSimple = Model("afeDutyCycleModelSimple",[DC],DutyCycle,"DutyCycle")
TXDutyCycleModelSimple = Model("TXDutyCycleModelSimple",[DC],DutyCycle,"DutyCycle")
mcuDCModelSimple = Model("mcuDutyCycleModelSimple",[DC],DutyCycle,"DutyCycle")

# Start of hierarchy definition. Components here are defined with Currents and their VDD (thus IV). Check out Component class for more info.
NVM = Component.IVDef("NVM",1e-3,150e-9,Vdd1,0)
Digital = Component.IVDef("Digital_Core_DVDD",600e-9,50e-9,Vdd2,1,[mcuDCModelSimple])

AFE_V_Channel_DVDD = Component.IVDef("AFE_V_Channel_DVDD",23.8e-9,23.8e-9,Vdd2,1)
AFE_V_Channel_AVDDL = Component.IVDef("AFE_V_Channel_AVDDL",65e-9,39e-9,Vdd2,1)
AFE_ADC_AVDDL = Component.IVDef("AFE_ADC_AVDDL",8.6e-9,1e-9,Vdd2,1)
AFE_V_Channel_AVDDH = Component.IVDef("AFE_V_Channel_AVDDH",7.48e-6,1e-9,Vdd1,1,[afeDutyCycleModelSimple])

TX = Component.IVDef("TX",3.4e-3,3.3e-9,Vdd1,1,[TXDutyCycleModelSimple])
                     
REG_VDD2 = VoltageRegulator.IVDef("REG_DVDD",VddIO, Vdd2,1,0,[Digital,AFE_V_Channel_DVDD,AFE_V_Channel_AVDDL,AFE_ADC_AVDDL],[],[])
REG_VDD1 = VoltageRegulator.IVDef("REG_AVDDH",VddIO, Vdd1,1,0,[AFE_V_Channel_AVDDH,TX, NVM],[],[])

# The top level Component-like object, which is in this case a ComponentGroup object. It could have been a Component or VoltageRegulator depending on how
# the user wanted to model the system top.
System_Top = ComponentGroup.IVDef("ASSIST_System_Top",VddIO,[],[],[REG_VDD1,REG_VDD2])
CF.updateHierarchy(System_Top)


#---------------- System Total Power and Sunburst Plot ---------------------
print("The total system power is currently:",System_Top.getTotalPower(),"uW.")
CF.sunburstPlot(System_Top)

# Using LogicalGroup class, we can group components across the hierarchy logically and combine their powers
LG_AFE = LogicalGroup("AFE",[AFE_V_Channel_DVDD,AFE_V_Channel_AVDDL,AFE_V_Channel_AVDDH],[],[])
LG_TX = LogicalGroup("TX",[TX],[],[])
LG_NVM = LogicalGroup("NVM",[NVM],[],[])
LG_MCU = LogicalGroup("MCU",[Digital],[],[])


#---------------- Duty-Cycle Plot --------------------------------
# Need to reassign the model that supports unitless duty-factor sweeps
AFE_V_Channel_AVDDH.setCurrentModel("afeDutyCycleModelSimple")
TX.setCurrentModel("TXDutyCycleModelSimple")
Digital.setCurrentModel("mcuDutyCycleModelSimple")
CF.updateHierarchy(System_Top)

# Generate plot
CF.dutyCyclePlotTable([System_Top,LG_AFE,LG_NVM,LG_TX,LG_MCU],DC,[None,0.01,None,0.001,0.1])

