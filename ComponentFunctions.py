# -*- coding: utf-8 -*-
"""
Created on 6/26/20
@author: Henry Bishop

ComponentFunctions: Module that contains common functions used for computing, sweeping, and plotting

Most Recent Update 7/4/20
- Created searchName, getHierarchyTotalPower, attrHierarchySweep, modelBasedSweep


Functions:

    Computing:
        convertNumber()
        updateHierarchy()
        sunburstPlotRecursion()
        searchName()
        getHierarchyTotalPower()

    Sweeping:
        attrHierarchySweep()
        modelBasedSweep()

    Plotting:
        sunburstPlot()


"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from Component import Component
from ComponentGroup import ComponentGroup
from VoltageRegulator import VoltageRegulator
from Variable import Variable
from Model import Model

_prefix = [["p","n","u","m","","k","M","G"],[1e-12,1e-9,1e-6,1e-3,1e0,1e3,1e6,1e9],[1e12,1e9,1e6,1e3,1e0,1e-3,1e-6,1e-9]]

def convertNumber(number,unit,round_value):
    """
    convertNumber: Return string that represents 'number' with proper SI prefix prepended to 'unit' (ex. W for power) as well as how many decimal places on the number.
    """
    length = len(_prefix[0][:])
    if number < _prefix[1][0]:
        return str(round(number*_prefix[2][0],round_value))+_prefix[0][0]+unit
    elif number > _prefix[1][length-1]:
        return str(round(number*_prefix[2][length-1],round_value))+_prefix[0][length-1]+unit
    else:
        for i in range(length-1):
            if (_prefix[1][i] <= number and number < _prefix[1][i+1]):
                return str(round(number*_prefix[2][i],round_value))+_prefix[0][i]+unit
    print("Error in convertNumber()")
    return

def updateHierarchy(thisComp):
    """
    updateHierarchy: after setting up desired "system architecture", this function merges all component-related objects into a single hierarchy
                     and updates TotalPower along the way for every component-related object
    """
    thisComp.clearHierarchy()   # Need to refresh hierarchy since we are appending things to it. Need to reset it.
    for comp in thisComp.components:
        #print(comp.name)
        comp.updateTotalPower()    # make sure total power is current for component
        #print(comp.TotalPower)
        thisComp.hierarchy["comp"] = np.append(thisComp.hierarchy["comp"],comp)
        #print(thisComp.hierarchy)
    for comp in thisComp.componentGroups:
        #print(comp.name)
        newComp = updateHierarchy(comp)
        newComp.updateTotalPower()  # update TotalPower based on new hierarchy
        #print(newComp.TotalPower)
        thisComp.hierarchy["compGroups"] = np.append(thisComp.hierarchy["compGroups"],newComp)
        #print(thisComp.hierarchy)
    for comp in thisComp.voltageRegulators:
        #print(comp.name)
        newComp = updateHierarchy(comp)
        newComp.updateTotalPower()  # update TotalPower based on new hierarchy
        #print(newComp.TotalPower)
        thisComp.hierarchy["vReg"] = np.append(thisComp.hierarchy["vReg"],newComp)
        #print(thisComp.hierarchy)
    thisComp.updateTotalPower()  # update TotalPower based on new hierarchy
    #print(thisComp.TotalPower)
    return thisComp

def sunburstPlotRecursion(thisComp):
    """
    sunburstPlotRecursion: First function in step to create starburst plot. Traverses hierarchy of components to grab parent, child, values from tree
    """
    parents = []
    children = []
    values = []
    for comp in thisComp.hierarchy["comp"]:
        parents.append(thisComp.name)
        children.append(comp.name)
        values.append(comp.TotalPower)
    for comp in thisComp.hierarchy["compGroups"]:
        parents.append(thisComp.name)
        children.append(comp.name)
        values.append(comp.TotalPower)
        newParents, newChildren, newValues = sunburstPlotRecursion(comp)
        parents.extend(newParents)
        children.extend(newChildren)
        values.extend(newValues)
    for comp in thisComp.hierarchy["vReg"]:
        parents.append(thisComp.name)
        children.append(comp.name)
        values.append(comp.TotalPower)
        parents.append(comp.name)
        children.append(comp.name+" Eff. Loss")
        values.append(comp.EffLossPower)
        parents.append(comp.name)
        children.append(comp.name+" Regulator Power")
        values.append(comp.RegPower)
        newParents, newChildren, newValues = sunburstPlotRecursion(comp)
        parents.extend(newParents)
        children.extend(newChildren)
        values.extend(newValues)
    #print("parents for",thisComp.name,":",parents)
    #print("children for",thisComp.name,":",children)
    #print("values for",thisComp.name,":",values)
    return parents, children, values

def sunburstPlot(thisComp=None,save=0,fileName=""):
    """
    sunburstPlot: Create Sunburst plot for hierarchical component showing breakdown weighted by TotalPower attributes. Should call updateHierarchy() before use.
    """
    parents, children, values = sunburstPlotRecursion(thisComp)
    parents.append("")
    children.append(thisComp.name)
    values.append(thisComp.TotalPower)
    hoverinfo = []
    hovertext = []
    for i in range(len(parents)):
        hovertext.append("<b>"+children[i]+"</b>"+"<br>"+"Power: "+str(convertNumber(values[i],"W",3)))
        hoverinfo.append("text")

    fig =go.Figure(go.Sunburst(
    name="",
    labels=children,
    parents=parents,
    values=values,
    branchvalues="total",
    hoverinfo=hoverinfo,
    hovertext=hovertext
    ))
    fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))
    fig.show()
    if(save == 1):
        fig.write_html(fileName+'.html',auto_open=True)

#To-Do: make function that will set an entire voltage rail to the same level since that may be something the user could sweep
#def setCommonVoltageRail():   

def searchName(thisComp,name):
    """
    searchName: searches for component with name within a hierarchy, returns number of levels it takes to get to component not including very top and the component
    """
    for comp in thisComp.hierarchy["comp"]:
        if(comp.getName() == name):
            return 1, comp

    for comp in thisComp.hierarchy["compGroups"]:   # Currently, componentGroups don't have attributes to be swept, so they only call the function to do deeper in the hierarchy
        subLevels, namedComp = searchName(comp,name)
        if(subLevels > 0):
            return (subLevels + 1), namedComp
        
    for comp in thisComp.hierarchy["vReg"]: # Regulators can be swept or the actual swept thing can be below it
        if(comp.getName() == name):
            return 1, comp
        else:
            subLevels, namedComp = searchName(comp,name)
            if(subLevels > 0):
                return (subLevels + 1), namedComp
    return 0, 0    # For the case that nothing is there, needs to return empty

def getHierarchyTotalPower(thisComp,name):
    """
    getHierarchyTotalPower: grabs all the TotalPower values from a specific component-like object and everything above it in the "tree"
    """
    for comp in thisComp.hierarchy["comp"]:
        if(comp.getName() == name):
            return True, [comp.getTotalPower()]

    for comp in thisComp.hierarchy["compGroups"]:   # Currently, componentGroups don't have attributes to be swept, so they only call the function to do deeper in the hierarchy
        valid, TP = getHierarchyTotalPower(comp,name)
        if valid:
            TP.append(comp.getTotalPower())
            return valid, TP
        
    for comp in thisComp.hierarchy["vReg"]: # Regulators can be swept or the actual swept thing can be below it
        if(comp.getName() == name):
            return True, [comp.getTotalPower()]
        else:
            valid, TP = getHierarchyTotalPower(comp,name)
            if valid :
                TP.append(comp.getTotalPower())
                return valid, TP
    return 0, 0    # For the case that nothing is there, needs to return empty

def attrHierarchySweep(name,attrKey,hierarchy,values,levels):
    """
    attrHierarchySweep: Based on component name, string name for attribute for sweep, hierarchical system, list of sweep values, and levels of hierarchy to report, will output TotalPower values
                        for each level of hierarchy for the sweep range/resolution
    """
    # 1) Search for component and save "coordinate" and check that levels value is valid given size of hierarchy
    # 2) for loop
    # 3) go to the component's coordinate, update first value based on attrKey
    # 4) update hierarchy
    # 5) save TotalPower in NxM array depending on levels input

    subLevels, comp = searchName(hierarchy, name)
    if levels != 'all':
        assert levels <= (subLevels + 1), "Input 'Levels' are greater than number of actual hierarchical levels"
    else: levels = subLevels + 1
    TPs = []
    for val in values:
        comp.setAttr(attrKey, val)
        updateHierarchy(hierarchy)
        valid, newTPs = getHierarchyTotalPower(hierarchy, name)
        if(not valid):
            return "attrHierarchySweep: Invalid total power hierarchy sweep"
        else:
            newTPs.append(hierarchy.getTotalPower())
            TPs.append(newTPs[0:levels])
    return TPs

def modelBasedSweep(compName, hierarchy, levels, model, variable):
    """
    modelBasedSweep: Allows a user to sweep a variable associated with a custom equation-based model to sweep parts of a hierarchy.
                    Uses the hierarchy, component name, model definition, and variable that should be swept all to generate three outputs:
                    1) the range of swept values for the variable 2) result of sweep from the equation-based model and
                    3) the TotalPower results from every level of hierarchy starting at the component being swept going all the way to the top level
    """
    X,Y = model.sweepFunction(variable)
    powers = attrHierarchySweep(compName,model.functionAttr,hierarchy,Y,levels)
    return X, Y, powers

def updateVariableList(thisComp):
    """
    updateVariableList: Takes a system hierarchy as input, locates all the relevant variables for the hierarchy based on CurrentModel parameter for Components,
                        then outputs a dictionary with keys that are the string variable names and values that are lists of "locations" for components
                        within the tree structure that use these variables so searching isn't required when updating values.
    """
    variables = {}
    for comp in thisComp.hierarchy["comp"]:
        if(comp.hasCurrentModel()):
            names = comp.CurrentModel.getVariableNames()
            for name in names:
                if(variables.get(name)): # If the key exists
                    variables[name] += [comp]
                else:
                    variables[name] = [comp]

    for comp in thisComp.hierarchy["compGroups"]:   # Currently, componentGroups don't have attributes to be swept, so they only call the function to do deeper in the hierarchy
        returnedVars = updateVariableList(comp) 
        for var in returnedVars:
            if var in variables:
                #merge them
                variables[var] += returnedVars[var]
            else:
                #add it
                variables[var] = returnedVars[var]
        
    for comp in thisComp.hierarchy["vReg"]: # Regulators can be swept or the actual swept thing can be below it
        returnedVars = updateVariableList(comp) 
        for var in returnedVars:
            if var in variables:
                #merge them
                variables[var] += returnedVars[var]
            else:
                #add it
                variables[var] = returnedVars[var]

    return variables

def variableSweep(hierarchy,variable):
    """
    variableSweep: Sweep the variable for the given hierarchy and report the resulting total power consumption for the hierarchy. The variable can be applied
                    to any number of independent components/models.
    """
    total_power = []
    variable.setSweepVals()
    vals = variable.getSweepVals()
    old_val = variable.getValue()
    for val in vals:
        variable.setValue(val)
        if(not(isinstance(hierarchy,Component))):   # Components dont have updateHierarchy function as its not needed
            updateHierarchy(hierarchy)
        else:
            hierarchy.updateTotalPower()
        total_power.append(hierarchy.getTotalPower())
    variable.setValue(old_val)
    return vals,total_power

def variableSweep2D(hierarchy, variable1, variable2):
    """
    variableSweep2D: 2D sweep for two separate variables. Row is variable 1 and column is variable 2.
    """
    i = 0
    vals1 = 0
    variable1.setSweepVals()
    variable2.setSweepVals()
    vals1_size = variable1.getSweepSize()
    vals2_size = variable2.getSweepSize()
    total_power = np.zeros((vals2_size,vals1_size))

    vals2 = variable2.getSweepVals()
    old_val = variable2.getValue()
    for val in vals2:
        variable2.setValue(val)
        if(not(isinstance(hierarchy,Component))):   # Components dont have updateHierarchy function as its not needed
            updateHierarchy(hierarchy)
        else:
            hierarchy.updateTotalPower()
        vals1,vals1_power = variableSweep(hierarchy,variable1)    
        total_power[i] = np.array(vals1_power)
        i += 1
    variable2.setValue(old_val)
    vals1 = np.array(vals1)
    vals2 = np.array(vals2)
    return vals1,vals2,total_power

def tuneVariable(hierarchy,component,variable,quantity=1,powerType="Relative"):
    """
    tuneVariable: Given a target power value, either relative to floor power or absolute (W) tune the provided variable such that a component's power consumption
    matches the target quantity. Update hierarchy object with this target value for the variable and return the variable value, component power, system power. This
    can be applied so the component is a Component, ComponentGroup, VoltageRegulator, or LogicalGroup object. Component could also be the hierarchy itself. In this way,
    the user can adjust a single variable and watch a single component's impact. They can instead achieve a target system power based on a single variable. They could 
    also just take part of a system and make it conform to a certain power value. ***Note: This variable could affect other components as well. This requires a 
    monotonic relationship between the variable and power consumption.
    """
    minIndex = 0
    diff = 0
    i = -1
    if(powerType == "Relative" or powerType == "Absolute"):
        if powerType == "Relative":
            # Determine target power first
            floorPower = hierarchy.getInactivePower()
            targetPower = quantity*floorPower
        elif powerType == "Absolute":
            targetPower = quantity
        vals,totalPower = variableSweep(component,variable)
        diff = abs(totalPower[0]-targetPower)
        for power in totalPower:
            i += 1
            if(abs(power-targetPower) < diff):
                diff = abs(power-targetPower)
                minIndex = i
        variable.setValue(vals[minIndex]) # set the value to the variable associated with the targetPower
        if(not(isinstance(component,Component))):   # Components dont have updateHierarchy function as its not needed
            updateHierarchy(component)
        else:
            component.updateTotalPower()
        updateHierarchy(hierarchy)
        return vals[minIndex],component.getTotalPower(),hierarchy.getTotalPower(),targetPower
    else:
        print("tuneVariable 'powerType' invalid")

def exchangeVariable(hierarchy,variable1,variable2,targetPower,delta):
    """
    exchangeVariable: delta is percentage of power allowable to be different
    """
    variable1.setSweepVals()
    variable2.setSweepVals()
    var1_vals = variable1.getSweepVals()
    
    orig_val1 = variable1.getValue()
    orig_val2 = variable2.getValue()

    variable1_result = np.array([])
    variable2_result = np.array([])
    deviation = np.array([])
    flag = 0

    for val1 in var1_vals:
        variable1.setValue(val1)
        vals,totalPower = variableSweep(hierarchy,variable2)
        totalPower = np.array(totalPower)
        sub = np.subtract(totalPower,np.repeat(targetPower,np.size(totalPower,0)))
        abs_vals = np.absolute(sub) # Absolute value of difference in arrays
        min_val = np.amin(abs_vals)
        if(min_val <= delta):
            if(flag < 2):
                flag = flag + 1
            index = np.where(abs_vals == min_val) # Calculates index to minimum power value, returns tuple
            variable2_result = np.append(variable2_result,vals[index[0][0]])
            variable1_result = np.append(variable1_result,val1)
            deviation = np.append(deviation,sub[index[0][0]])

    if(flag == 0):
        print("exchangeVariable: Target power not achievable.")

    if(flag == 1):
        print("exchangeVariable: Target power only achievable at one point: (",variable1_result[0],",",variable2_result[0],")")

    variable1.setValue(orig_val1)
    variable2.setValue(orig_val2)
    return variable1_result,variable2_result,deviation

def dutyCyclePlot(hierarchies,DC_Variable,points=[]):
    """
    dutyCyclePlot: Takes list of components to plot, the duty cycle variable, and specific duty cycle values to plot as operating points per component.
    It will plot duty cycle versus power for each component and if points are provided then put them on the curve.
    """
    # print(len(hierarchies))
    # print(type(DC_Variable.getSweepSize()))

    results = np.empty((len(hierarchies),DC_Variable.getSweepSize()))
    i = 0
    fig = go.Figure()
    for comp in hierarchies:
        results = variableSweep(comp,DC_Variable)
        fig.add_trace(go.Scatter(x=results[0], y=results[1], mode='lines', name=comp.getName()))
        if(len(points) == len(hierarchies)):
            if(points[i] != None):
                DC_Variable.setValue(points[i])
                updateHierarchy(comp)
                temp_power = comp.getTotalPower()
                fig.add_trace(go.Scatter(x=[points[i]], y=[temp_power], mode='markers', marker={'size':10, 'color':'black'},showlegend=False))
        i = i + 1

    #fig.add_trace(go.Scatter(x=[0.5], y=[1e-6], mode='markers', name='temp', marker=dict(size=10)))
    fig.update_layout(title="Duty-Cycle Model",
                    xaxis_title='Duty-Cycle',
                    yaxis_title='Average Power (W)',
                    xaxis=dict(type='log',exponentformat='power',dtick='1'),
                    yaxis=dict(type='log',exponentformat='SI',dtick='1'))
    fig.show()
    #fig.write_html('Figures/system.html',auto_open=True)

def dutyCyclePlotTable(hierarchies,DC_Variable,points=[]):
    """
    dutyCyclePlot: Takes list of components to plot, the duty cycle variable, and specific duty cycle values to plot as operating points per component.
    It will plot duty cycle versus power for each component and generate a separate table for specified points.
    """

    fig = make_subplots(
    rows=2, cols=1,
    specs=[[{"type": "scatter"}],[{"type": "table"}]])
    results = np.empty((len(hierarchies),DC_Variable.getSweepSize()))
    table_names = []
    table_data = []
    i = 0
    for comp in hierarchies:
        results = variableSweep(comp,DC_Variable)
        fig.append_trace(go.Scatter(x=results[0], y=results[1], mode='lines', name=comp.getName()), row=1, col=1)
        if(len(points) == len(hierarchies)):
            if(points[i] != None):
                DC_Variable.setValue(points[i])
                updateHierarchy(comp)
                temp_power = comp.getTotalPower()
                table_names.append(comp.getName())
                table_data.append(convertNumber(temp_power,'W',1))
                fig.append_trace(go.Scatter(x=[points[i]], y=[temp_power], mode='markers', marker={'size':10, 'color':'black'},showlegend=False),row=1, col=1)
        i = i + 1

    fig.append_trace(go.Table(header=dict(values=['Name', 'Average Power (W)']),
                                    cells=dict(values=np.array([table_names,table_data]))),row=2, col=1)

    #fig.add_trace(go.Scatter(x=[0.5], y=[1e-6], mode='markers', name='temp', marker=dict(size=10)))
    fig.update_layout(title="Duty-Cycle Model",
                    xaxis_title='Duty-Cycle',
                    yaxis_title='Average Power (W)',
                    xaxis=dict(type='log',exponentformat='power',dtick='1'),
                    yaxis=dict(type='log',exponentformat='SI',dtick='1'))
    fig.show()
    #fig.write_html('Figures/system.html',auto_open=True)

def dutyCycleVariablePlot(hierarchies,DC_Variable,points=[],variables=[],models=[],variableComponents=[]):
    """
    Same as dutyCyclePlot function, but also incorporates ability to plot a color gradient plot relative to the value of another variable per component.
    Variables to be swept must be in the same order as the components in the hierarchy.

    variableComponents should hold all the components that need setCurrentModel redone for them [[comp1, comp2],[comp_a, comp_b],...] where the dimensions 
    are X by Y, X = (rows) number of components that need to be reset per variable, Y = (columns) number of variables. There is one variable per hierarchy.

    Models are needed because as we sweep one variable, we need to update the component with the specific model

    """
    #results = np.empty((len(hierarchies),DC_Variable.getSweepSize()))
    i = 0
    pad = 0
    fig = go.Figure()
    for comp in hierarchies:
        results = variableSweep(comp,DC_Variable)
        fig.add_trace(go.Scatter(x=results[0], y=results[1], mode='lines', name=comp.getName()))
        if(len(points) == len(hierarchies)):
            if(points[i] != None):
                DC_Variable.setValue(points[i])
                updateHierarchy(comp)
                temp_power = comp.getTotalPower()
                fig.add_trace(go.Scatter(x=[points[i]], y=[temp_power], mode='markers', marker={'size':10, 'color':'black'},showlegend=False))
        if(len(variables) == len(hierarchies) and len(variableComponents[:]) == len(hierarchies) and len(models) == len(hierarchies)):
            if(variables[i] != None):
                # need to reset the components to be driven by this variable and not duty cycle
                j = 0
                for comps in variableComponents[i]:
                    comps.setCurrentModel(models[i][j].getName())   # Each component may end up having different models, we will only plot against one variable though
                    print(models[i][j].getName())
                    j = j + 1
                results_custom = variableSweep(comp,variables[i])  # still sweep the hierarchy
                print(variables[i].getName())
                print(comp.getName())
                # The model outupt should be in units of DUTY CYCLE which is why they can be on the same x axis!!!!
                # The first model will be the one that is presented
                var_output, model_output = models[i][0].sweepFunction(variables[i])
                fig.add_trace(go.Scatter(x=model_output, y=results_custom[1],mode='markers', showlegend=False, marker={'color': var_output, 
                                        'colorscale': 'Plasma', 'size': 10, 'showscale':True, 
                                        'colorbar':{'ticks':"outside",'ticksuffix':variables[i].getUnit(), 'xpad':pad,
                                        'title': {'text':variables[i].getName()} }}))
                pad = pad + 150
        i = i + 1

    #fig.add_trace(go.Scatter(x=[0.5], y=[1e-6], mode='markers', name='temp', marker=dict(size=10)))
    fig.update_layout(title="Duty-Cycle Model",
                    xaxis_title='Duty-Cycle',
                    yaxis_title='Average Power (W)',
                    xaxis=dict(type='log',exponentformat='power',dtick='1'),
                    yaxis=dict(type='log',exponentformat='SI',dtick='1'),
                    legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                ))
    fig.show()
    #fig.write_html('Figures/system.html',auto_open=True)

def contourVariablePlot(hierarchy, variable1, variable2):
    vals1,vals2,power = variableSweep2D(hierarchy, variable1, variable2)
    fig = go.Figure()
    fig.add_trace(go.Contour(z=power,x=vals1,y=vals2,
        colorbar=dict(
            exponentformat='SI'
        ),
        contours=dict(
                coloring ='heatmap',
                showlabels = True, # show labels on contours
                labelfont = dict( # label font properties
                    size = 12,
                    color = 'white',
                ))))
    title = "Contour Variable Plot: "+hierarchy.getName()
    fig.update_layout(title=title,
                    xaxis_title=variable1.getName(),
                    yaxis_title=variable2.getName()
                    )
    fig.show()
    #fig.write_html('Figures/system.html',auto_open=True)

def getLifetime(hierarchy,energy,unit):
    """
    getLifetime: reports back lifetime in seconds, minutes, hours, days, weeks, months, years given a specific energy budget
    """
    divider_map = {
        'second':1,
        'minute':60,
        'hour':3600,
        'day':3600*24,
        'week':3600*24*7,
        'month':3600*24*30,
        'year':3600*24*365
    }

    if(unit not in divider_map):
        print("getLifetime: unit doesn't have proper name")
    
    else:
        if(not(isinstance(hierarchy,Component))):   # Components dont have updateHierarchy function as its not needed
            updateHierarchy(hierarchy)
        else:
            hierarchy.updateTotalPower()
        return energy/(divider_map[unit]*hierarchy.getTotalPower())

def sweepLifetime(hierarchy,energy,variable,unit):
    """
    sweepLifetime: reports back a sweep of lifetimes in seconds, minutes, hours, days, weeks, months, years given a specific energy budget
    """
    divider_map = {
        'second':1,
        'minute':60,
        'hour':3600,
        'day':3600*24,
        'week':3600*24*7,
        'month':3600*24*30.42,
        'year':3600*24*365.2425
    }

    if(unit not in divider_map):
        print("sweepLifetime: unit doesn't have proper name")
    
    else:
        vals,totalpower = variableSweep(hierarchy,variable)
        lifetime = energy/divider_map[unit]*np.divide(np.ones((1,variable.getSweepSize())),totalpower)
        lifetime = lifetime[0][:]
        return vals,lifetime

def sweepLifetime2D(hierarchy,energy,variable1,variable2,unit):
    """
    sweepLifetime2D: reports back a 2D sweep of lifetimes in seconds, minutes, hours, days, weeks, months, years given a specific energy budget
    """
    divider_map = {
        'second':1,
        'minute':60,
        'hour':3600,
        'day':3600*24,
        'week':3600*24*7,
        'month':3600*24*30.42,
        'year':3600*24*365.2425
    }

    if(unit not in divider_map):
        print("sweepLifetime: unit doesn't have proper name")
    
    else:
        vals1,vals2,totalpower = variableSweep2D(hierarchy,variable1,variable2)
        lifetime = energy/divider_map[unit]*np.divide(np.ones((variable2.getSweepSize(),variable1.getSweepSize())),totalpower)
        lifetime = lifetime[0][:]
        return vals1,vals2,lifetime

def contourLifetimePlot(hierarchy,energy,variable1,variable2,unit):
    vals1,vals2,lifetime = sweepLifetime2D(hierarchy,energy,variable1,variable2,unit)
    fig = go.Figure()
    fig.add_trace(go.Contour(z=lifetime,x=vals1,y=vals2,
        colorbar=dict(
            exponentformat='SI'
        ),
        contours=dict(
                coloring ='heatmap',
                showlabels = True, # show labels on contours
                labelfont = dict( # label font properties
                    size = 12,
                    color = 'white',
                ))))
    title = "Contour Lifetime Plot: "+hierarchy.getName()
    fig.update_layout(title=title,
                    xaxis_title=variable1.getName(),
                    yaxis_title=variable2.getName()
                    )
    fig.show()
    #fig.write_html('Figures/system.html',auto_open=True)

def plotXY(X=None,Y=None,Title=None,X_Label=None,Y_Label=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=X, y=Y,mode='lines',name=Title))
    fig.update_layout(title=Title,
                    xaxis_title=X_Label,
                    yaxis_title=Y_Label
                    )
    fig.show()