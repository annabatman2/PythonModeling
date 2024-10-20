# -*- coding: utf-8 -*-
"""
Created on 2/24/21
@author: Henry Bishop

This is an example system model to demo 1) the method for setting up a system hierarchy with this modeling framework and 2) a variety of useful functions built to help
users analyze the system. This model is based upon the low-power system designed for the NSF ASSIST Center. It includes definitions models related to 1) a processor and 
memory core (Digital Core), 2) an analog front-end (AFE), 3) BLE compliant transmitter (TX), and 4) nonvolatile memory (NVM).

**NOTE** The plotting functionality used here should create new browser windows and it will generate quite a few of them if this file is unchanged. There is one quirk
that you may encounter where the plot doesn't seem to show up in the browser. In this case, it will act as if it's loading something. If this happens, then click
on the address bar and then hit "Enter". This should make it load.

Plotly setup when using Anaconda:
    -- to install plotly (e.g. at spyder prompt): conda install -c plotly plotly=4.8.2
    -- to setup display (e.g. at spyder prompt):
        import plotly.io as pio
        pio.renderers?
        pio.renderers.default='browser'

"""
from Component import Component
from ComponentGroup import ComponentGroup
from LogicalGroup import LogicalGroup
from VoltageRegulator import VoltageRegulator
from Variable import Variable
from Model import Model
from Mode import Mode
import ComponentFunctions as CF
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "browser"

# Notes about model quirks
# - active power shouldn't be listed as zero, it should be at least the leakage power if not listed, meaning that there is no active component it just stays at leakage level

# Four voltage rails are provided by a power management unit
DVDD = 0.6
AVDDL = 0.6
AVDDH = 1.2
VDDIO = 3.3

# Variable definition for AFE
AFE_On_Time = Variable("AFE_On_Time",1e-3)
AFE_Sampling_Rate = Variable("AFE_Sampling_Rate",50,0.1,100,0.5,"Hz")

# Variable definition for TX
TX_On_Time = Variable("TX_On_Time",(600e-6*2))
TX_Rate = Variable("TX_Rate",1,1/10,5,0.1,"Hz")

# Python function that models relationship between AFE and TX variables to produce their respective duty-cycle factors
# ** NOTE ** The user has total control over what happens here. Variables can relate to hardware power consumption in a variety of ways and can be
# modeled in a variety of ways. Only Component objects are associated with specific models/variables like this. Look into the Model class for more info
# and specifically "setAttr" method in Component class for alternatives to calculating dutyCycle (ex. TotalPower, InactiveCurrent, ...).

def AFEDutyCycle(varDictionary):
    AFE_On_Time = varDictionary["AFE_On_Time"].value
    AFE_Sampling_Rate = varDictionary["AFE_Sampling_Rate"].value
    dutyCycle = AFE_On_Time*AFE_Sampling_Rate
    return dutyCycle

def TXDutyCycle(varDictionary):
    TX_On_Time = varDictionary["TX_On_Time"].value
    TX_Rate = varDictionary["TX_Rate"].value
    dutyCycle = TX_On_Time*TX_Rate
    return dutyCycle


# A generic variable and function to represent duty-cycle
DC = Variable("Duty_Cycle",1,0.0001,1,0.0001)

def DutyCycle(varDictionary):
    dutycycle = varDictionary["Duty_Cycle"].value
    return dutycycle

# Creating several Models objects to represent AFE and TX duty-cycle
afeDutyCycleModelSimple = Model("afeDutyCycleModelSimple",[DC],DutyCycle,"DutyCycle")
TXDutyCycleModelSimple = Model("TXDutyCycleModelSimple",[DC],DutyCycle,"DutyCycle")
afeDutyCycleModel = Model("afeDutyCycleModel",[AFE_On_Time,AFE_Sampling_Rate],AFEDutyCycle,"DutyCycle")
TXDutyCycleModel = Model("TXDutyCycleModel",[TX_On_Time,TX_Rate],TXDutyCycle,"DutyCycle")

# Start of hierarchy definition. Components here are defined with Currents and their VDD (thus IV). Check out Component class for more info.
NVM = Component.IVDef("NVM",1e-3,150e-9,VDDIO,0)
Digital_Core_DVDD = Component.IVDef("Digital_Core_DVDD",600e-9,50e-9,DVDD,1)
Digital_Clock_AVDDL = Component.IVDef("Digital_Clock_AVDDL",25e-9,1e-9,AVDDL,1)
Digital_AVDDH_SPI = Component.IVDef("Digital_AVDDH_SPI",128e-9,90e-9,AVDDH,1) # Should be swept
Digital_AVDDH_Extra = Component.IVDef("Digital_AVDDH_Extra",(10e-9+15e-9+6e-9+31e-9),(10e-9+15e-9+6e-9+31e-9),AVDDH,0)

AFE_V_Channel_DVDD = Component.IVDef("AFE_V_Channel_DVDD",23.8e-9,23.8e-9,DVDD,1)
AFE_V_Channel_AVDDL = Component.IVDef("AFE_V_Channel_AVDDL",65e-9,39e-9,AVDDL,1)
AFE_ADC_AVDDL = Component.IVDef("AFE_ADC_AVDDL",8.6e-9,1e-9,AVDDL,1)
AFE_V_Channel_AVDDH = Component.IVDef("AFE_V_Channel_AVDDH",7.48e-6,1e-9,AVDDH,1,[afeDutyCycleModelSimple,afeDutyCycleModel]) # Should be swept

TX = Component.IVDef("TX",3.4e-3,3.3e-6,AVDDH,1,[TXDutyCycleModelSimple,TXDutyCycleModel]) # Should be swept

REG_DVDD = VoltageRegulator.IVDef("REG_DVDD",VDDIO,DVDD,1,0,[Digital_Core_DVDD,AFE_V_Channel_DVDD],[],[])
REG_AVDDL = VoltageRegulator.IVDef("REG_AVDDL",VDDIO,AVDDL,1,0,[Digital_Clock_AVDDL,AFE_V_Channel_AVDDL,AFE_ADC_AVDDL],[],[])
REG_AVDDH = VoltageRegulator.IVDef("REG_AVDDH",VDDIO,AVDDH,1,0,[AFE_V_Channel_AVDDH,Digital_AVDDH_Extra,Digital_AVDDH_SPI,TX],[],[])
REG_VDDIO = VoltageRegulator.IVDef("REG_VDDIO",VDDIO,VDDIO,1,0,[NVM],[],[])

# The top level Component-like object, which is in this case a ComponentGroup object. It could have been a Component or VoltageRegulator depending on how
# the user wanted to model the system top.
ASSIST_System_Top = ComponentGroup.IVDef("ASSIST_System_Top",VDDIO,[],[],[REG_DVDD,REG_AVDDL,REG_AVDDH,REG_VDDIO])
CF.updateHierarchy(ASSIST_System_Top)

# Create a mode to describe standard operation for the system - comprises of models for AFE and TX
normalMode = Mode("NormalMode",[AFE_V_Channel_AVDDH,TX],["afeDutyCycleModel","TXDutyCycleModel"],ASSIST_System_Top)

#---------------- System Total Power and Sunburst Plot ---------------------
print("The total system power is currently:",ASSIST_System_Top.getTotalPower(),"uW.")
CF.sunburstPlot(ASSIST_System_Top)


#---------------- Simple Variable Sweep --------------------------------
x,y = CF.variableSweep(ASSIST_System_Top,TX_Rate)
CF.plotXY(x,y,"System Power Consumption","TX Rate (Hz)","Power (W)")

#---------------- 2D Variable Sweep --------------------------------
CF.contourVariablePlot(ASSIST_System_Top,TX_Rate,AFE_Sampling_Rate)

#---------------- 2D Lifetime Sweep --------------------------------
CF.contourLifetimePlot(ASSIST_System_Top,(1/2*100e-3*3.3**2),TX_Rate,AFE_Sampling_Rate,"day")

#---------------- Tune Variable --------------------------------
# Goal is to tune the TX_Rate variable until the system achieves a desired level of power consumption. This can be 
# relative to the system floor level as shown here or as an absolute value in Watts.
var,compPower,sysPower,target = CF.tuneVariable(ASSIST_System_Top,ASSIST_System_Top,TX_Rate,3,"Relative")
print("----------Tune Variable-----------")
print("TX Rate adjusted to",var,"Hz")
print("Achieved system power is",sysPower,"W")
print("Target power was",target,"W")
print("----------------------------------")

#---------------- Exchange Variable --------------------------------
# Goal is to plot the trade-off between two variables while maintaining constant system power consumption
sys_target_power = 15e-6
allowable_deviation = 1e-6
temp = CF.convertNumber(sys_target_power,"W",1)
title = "TX and AFE Variable Trade-Off for System Power of "+temp
var1,var2,deviation = CF.exchangeVariable(ASSIST_System_Top,TX_Rate,AFE_Sampling_Rate,sys_target_power,allowable_deviation)
CF.plotXY(var1,var2,title,"TX Rate","AFE Sampling Rate")


#---------------- Duty-Cycle Plot --------------------------------
# Need to reassign the model that supports unitless duty-factor sweeps
AFE_V_Channel_AVDDH.setCurrentModel("afeDutyCycleModelSimple")
TX.setCurrentModel("TXDutyCycleModelSimple")
CF.updateHierarchy(ASSIST_System_Top)

# Using LogicalGroup class, we can group components across the hierarchy logically and combine their powers
LG_AFE = LogicalGroup("AFE",[AFE_V_Channel_DVDD,AFE_V_Channel_AVDDL,AFE_V_Channel_AVDDH],[],[])
LG_TX = LogicalGroup("TX",[TX],[],[])
LG_NVM = LogicalGroup("NVM",[NVM],[],[])
LG_MCU = LogicalGroup("MCU",[Digital_Core_DVDD],[],[])

# Generate plot
CF.dutyCyclePlotTable([ASSIST_System_Top,LG_AFE,LG_NVM,LG_TX,LG_MCU],DC,[None,0.01,None,0.001,None])

#More complex duty-cycle plot that shows variable values
CF.dutyCycleVariablePlot([LG_TX,LG_AFE,LG_NVM,LG_MCU],DC,[],[TX_Rate,AFE_Sampling_Rate,None,None],[[TXDutyCycleModel],[afeDutyCycleModel],[None],[None]],[[TX],[AFE_V_Channel_AVDDH],[None],[None]])