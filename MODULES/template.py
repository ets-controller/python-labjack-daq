# -*- coding: utf-8 -*-
"""
Created on Wed May  6 12:31:43 2020

@author: lucasd

This script can be used as a template
The three main elements of a LabJack sensor module appear in this script: multiple sensors, differential measurements, and extended features
It is setup to read two Pheiffer Full-Range Gauges [torr] differentially across AIN0-1 and AIN2-3 by using the offset/slope extended feature 
The decibal value Y is recorded, where P = 10^Y and Y = Ax+B 

"""
###############################################################################
# The number of sensors that use this module
numSEN = 2
# Returns the sensor names
def names():
    names = ['SEN']
    return names
# Returns the number of sensors
def number(item):
    if item == 'SEN':
        return numSEN
        
###############################################################################  
# Assigns sensors to AIN through channels and registries, does extended features math
def main(handle):
    from labjack import ljm
    aAddresses = {}
    aDataTypes = {}
    aValues = {}
    # Setup and call eReadAddresses to read values from the LabJack.
    aAddresses['SEN'] = []  # [Sensor Reading]
    aAddresses['Voltage_SEN'] = [] # [Sensor Voltage]
    aDataTypes['SEN'] = [] # [Data types for the Sensor and Voltage]
    
###############################################################################
    # AIN for SEN
    # For base differential channels, positive must be an even channel from 0-12 and negative must be positive+1
    AINp = 0 # The positive lead is in AIN0
    AINn = AINp+1 # The negaitve lead is in AIN1
    # Using a relationship for the positive and negative leads is useful for writting loops to assign values to multiple sensors using the same module
    # I.E., loop over numSEN
    
    # What registers will be used?
    # Search LabJack documentation for 'AIN Extended Features' to find the register translation table
    # In this example we want to scale a voltage value by an offset and slope
    # Registers 90XX store the EF_INDEX: 1 for offset and slope
    # Registers 102XX store the EF_CONFIG_D: the slope
    # Registers 105XX store the EF_CONFIG_E: the offset
    REG = [9000,10200,10500]
    
    # What values should be stored in the registry?
    # Converts the SEN Voltage to the form Ax+B
    A = 10/6;B = -10/6*6.8
    VAL = [1,A,B] # What values should be written to each register address
    #VAL = [1,1,0] # These values are for a unitary operation
    TYPE = [1,3,3] # What number type will be written? 1:UINT32, 3:FLOAT32
    ###############################################################################
    
    # Clear EF dictionary entries
    aAddresses['AIN#_EF_INDEX'] = []  # [Set EF type address]
    aDataTypes['AIN#_EF_INDEX'] = []  # [Set EF type as int]
    aValues['AIN#_EF_INDEX'] = []  # [Set EF type, 1 for offset/slope]
    # Initialize EF negative channel
    aAddresses['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel for differential measurement]
    aDataTypes['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel type as int]
    aValues['AIN#_NEGATIVE_CH'] = []  # [Set EF negative channel]
    
    for i in range numSEN:
        # Write EF parameters: loop over VAL
        for j in range(len(VAL)):
            aAddresses['AIN#_EF_INDEX'].append(REG[j]+2*(2*i+AINp)) # Add the register address to the aAddresses dictionary. 2*i+AINp for even channels starting with the first positive channel, e.g., AIN0, AIN2, AIN4,..., and 2* because the register address is even, e.g., EF_INDEX_AIN0:9000, EF_INDEX_AIN1:9002,...
            aValues['AIN#_EF_INDEX'].append(VAL[j]) # Write the value to the aValues dictionary
            aDataTypes['AIN#_EF_INDEX'].append(TYPE[j]) # Add the register type to the aDataTypes dictionary
        # Write Differential Measurement parameters
        aAddresses['AIN#_NEGATIVE_CH'].append(41000+2*i+AINp) # Register that specifies the negative channel to be used for each positive channel. 2*i+AINn for odd channels starting with the first negative channel, e.g., AIN1, AIN3, AIN5,...
        aValues['AIN#_NEGATIVE_CH'].append(2*i+AINn) # What is the negative channel. 2*i+AINn for odd channels starting with the first negative channel, e.g., AIN1, AIN3, AIN5,...
        aDataTypes['AIN#_NEGATIVE_CH'].append(ljm.constants.UINT16) # What is the type

    # Write to LabJack
    ljm.eWriteAddresses(handle, len(aAddresses['AIN#_EF_INDEX']), aAddresses['AIN#_EF_INDEX'], aDataTypes['AIN#_EF_INDEX'], aValues['AIN#_EF_INDEX']) # Write the EF params to the LabJack
    ljm.eWriteAddresses(handle, len(['AIN#_NEGATIVE_CH']), aAddresses['AIN#_NEGATIVE_CH'], aDataTypes['AIN#_NEGATIVE_CH'], aValues['AIN#_NEGATIVE_CH']) # Write the Differential Measurement params to the LabJack
    # Write address for EF value
    for i in range numSEN:
        aAddresses['SEN'].append(7000+2*(2*i+AINp)) # This is where the sensor value is stored. 2*i+AINp for even channels starting with the first positive channel, e.g., AIN0, AIN2, AIN4,..., and 2* because the register address is even, e.g., EF_INDEX_AIN0:7000, EF_INDEX_AIN1:7002,...
        aAddresses['Voltage_SEN'].append(7300+2*(2*i+AINp)) # This is where the voltage value is stored. 2*i+AINp for even channels starting with the first positive channel, e.g., AIN0, AIN2, AIN4,..., and 2* because the register address is even, e.g., EF_INDEX_AIN0:7300, EF_INDEX_AIN1:7302,...
        aDataTypes['SEN'].append(ljm.constants.FLOAT32)
    return aAddresses, aDataTypes, aValues
    ###########################################################################


























