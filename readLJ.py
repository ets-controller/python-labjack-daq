# -*- coding: utf-8 -*-
"""
Created on Wed May  6 11:20:51 2020

@author: lucasd
"""
import os
import time
import subprocess
import sys
import datetime as dt
from labjack import ljm

# Magic numbers
# Input scan rate
scanRate = 1 # Hz
scanTime = 1/scanRate # s
# Get current timestamp
ts = [0,0,0];ts[0] = time.time()
today = dt.date.today().strftime("%Y-%m-%d")
fstr = 'LJdata_'
tstr = 'timestamp'    
rowSpace = 0
colSpace = 0

# Setup environment
# Define the path and output directories
PATH = os.getcwd()
DATA = os.path.join(PATH,'DATA')
MODULES = os.path.join(PATH,'MODULES')
PLOTS = os.path.join(PATH,'PLOTS')

# Make the directory for the data and plots
if not os.path.exists(DATA):
    os.mkdir(DATA)
if not os.path.exists(MODULES):
    os.mkdir(MODULES)
if not os.path.exists(PLOTS):
    os.mkdir(PLOTS)

# Add the modules to the system path
sys.path.append(MODULES)

# Add the sensor modules
import thermocouple
import level
import frg

# Find the names of the sensors and how many there are
sensor = {}
sensor['names'] = []
sensor['ident'] = []
for name in thermocouple.names():
    sensor['names'].append(name)
    sensor['num%s'%name] = thermocouple.number(name)
    for num in range(sensor['num%s'%name]):
        sensor['ident'].append(name+'%s'%(num+1))
for name in level.names():
    sensor['names'].append(name)
    sensor['num%s'%name] = level.number(name)
    for num in range(sensor['num%s'%name]):
        sensor['ident'].append(name+'%s'%(num+1))
for name in frg.names():
    sensor['names'].append(name)
    sensor['num%s'%name] = frg.number(name)
    for num in range(sensor['num%s'%name]):
        sensor['ident'].append(name+'%s'%(num+1))

# Pass values to buffer
def buffer_output():
    return DATA, LOG, fstr, scanRate, chunkTime, tstr, sensor['ident']
def cache_output():
    return DATA, CRASH

##############################################################################
# COMPACT THIS SECTION #######################################################       
##############################################################################

# Data stream and record
results = {}
if __name__ == '__main__':
    
    # LJ setup
    # Connect to the labjack
    LJ_dict = {}
    LJ_dict['handle_1'] = ljm.openS("any", "any", "470019751")  # [TC, K] device type, connection type, serial no.
    LJ_dict['handle_2'] = ljm.openS("ANY", "ANY", "470019220")  # [RES, FRG] device type, connection type, serial no.

    # Get LJ handle
    LJ_dict['info_1'] = ljm.getHandleInfo(LJ_dict['handle_1'])
    LJ_dict['info_2'] = ljm.getHandleInfo(LJ_dict['handle_2'])

    # Create dictionaries to store channel/registry information
    aAddresses, aDataTypes, aValues = {},{},{}

    # Find the channel/registry information for each of the sensor suites
    aAddresses.update(thermocouple.main(LJ_dict['handle_1'])[0]);aDataTypes.update(thermocouple.main(LJ_dict['handle_1'])[1]);aValues.update(thermocouple.main(LJ_dict['handle_1'])[2])
    aAddresses.update(level.main(LJ_dict['handle_2'])[0]);aDataTypes.update(level.main(LJ_dict['handle_2'])[1]);aValues.update(level.main(LJ_dict['handle_2'])[2])
    aAddresses.update(frg.main(LJ_dict['handle_2'])[0]);aDataTypes.update(frg.main(LJ_dict['handle_2'])[1]);aValues.update(frg.main(LJ_dict['handle_2'])[2])
                    
    # Launch buffer
    #subprocess.run('python3 __buffer__.py &',shell=True)
    
    # Launch DAQ Loop
    while True:

        # Get time and define datafile
        ts[1] = time.time()
        shortname = 'LJdata.csv'
        filename = os.path.join(DATA,shortname)

        # Create the datafile
        if not os.path.exists(filename):
            f = open(filename,'w+')
            f.close()

        # Write to the datafile
        if os.path.exists(filename):
            for name in sensor['names']:
                if name in thermocouple.names():
                    results[name] = ljm.eReadAddresses(LJ_dict['handle_1'], sensor['num%s'%name], aAddresses[name], aDataTypes[name])
                if name in frg.names() or name in level.names():
                    results[name] = ljm.eReadAddresses(LJ_dict['handle_2'], sensor['num%s'%name], aAddresses[name], aDataTypes[name])
	    # Open the file
            f = open(filename,'w')
	    # Write the column headers
            f.write("%s"%tstr)
            for strname in sensor['ident']:
                f.write(";%s"%strname)
	    # Write the sensor value
            f.write("\n%0.1f"%ts[1])
            colSpace = 1
            for name in sensor['names']:
                for j in range(sensor['num%s'%name]):
                    f.write(";%0.5f"%results[name][j])
                    colSpace += 1
            f.close()
            rowSpace += 1

        # Wait until end of scanPeriod
        ts[2] = time.time()
        procTime = ts[2]-ts[1]
        if (scanTime-procTime) > 0:
            waitTime = scanTime-procTime
            time.sleep(waitTime)

