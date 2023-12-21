import os
import time
import csv
import numpy as np
from readLJ import buffer_output

# Define scanRate and avgTime
scanRate, avgTime, bufferSize = buffer_output()[2], 30, 30*60 # Seconds

# Delete the buffer file if it exists
if os.path.exists('DATA/LJbuffer.csv'):
    os.remove('DATA/LJbuffer.csv')

# Open the data file and grab the header
data = np.genfromtxt('DATA/LJdata.csv', delimiter=';', names=True)
header = data.dtype.names

# Open the buffer file and write the header
with open('DATA/LJbuffer.csv','w') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(header)
f.close()

# Define a temporary array for each name in the header
avgArray = {};avgVal = {}
for name in header:
    avgArray[name] = np.array([])

# Open the LJdata file at a rate of scanRate and grab the data
while True:
    # Get the time
    ts = time.time()

    # Get the new data
    data = np.genfromtxt('DATA/LJdata.csv', delimiter=';', names=True)
    # Append the new data to the temporary array
    for name in header:
        avgArray[name] = np.append(avgArray[name],data[name])
        # If there are more than avgTime worth of data points, average the data and append to the buffer file
        if len(avgArray[name]) >= int(avgTime):
            # Average the data and store it as a key-item pair in a dictionary which is associated with the header
            avgVal[name] = np.mean(avgArray[name])
            # Clear the temporary array
            avgArray[name] = np.array([])
            # Open the buffer file and append the data
            # If the name is the last in the header, add a newline
            if name == header[-1]:
                with open('DATA/LJbuffer.csv','a') as f:
                    f.write('%.5f\n'%avgVal[name])
                    f.close()
            # Otherwise, add a semicolon
            else:
                with open('DATA/LJbuffer.csv','a') as f:
                    f.write('%.5f;'%avgVal[name])
                    f.close()   
    # Check if there are more than 3 data points in the buffer file, if there is

    # If there are more than 30 minutes worth of data points in the buffer, delete the oldest data point
    # Check how many rows are in the buffer file, excluding the header
    with open('DATA/LJbuffer.csv','r') as g:
        reader = csv.reader(g, delimiter=';')
        row_count = sum(1 for row in reader)-1
        g.close()

    # Check if the buffer is full
    #if row_count >= int(bufferSize/avgTime):
    if row_count >= int(3):
        # Open the buffer file and delete the first row
        with open('DATA/LJbuffer.csv','r') as g:
            reader = csv.reader(g, delimiter=';')
            # If there are more than 30 minutes worth of data points, delete the oldest data point
            if row_count >= int(bufferSize/avgTime):
                # Skip the header
                next(reader)
                # Skip the first row
                next(reader)
                # Open the buffer file and write the data
                with open('DATA/LJbuffer.csv','w') as f:
                    writer = csv.writer(f, delimiter=';')
                    # Write the header
                    writer.writerow(header)
                    # Write the data
                    for row in reader:
                        writer.writerow(row)
                    f.close()
            g.close()
        # Calculate the derivative of RES1 through RES7 as a function of time (timestamp)
        # Open the buffer file and grab the data
        buffer = np.genfromtxt('DATA/LJbuffer.csv', delimiter=';', names=True)
        # Create a dictionary to store the derivative of each sensor
        sigproc = {}
        # Copy the data from the buffer file to the sigproc dictionary
        for name in header:
            sigproc[name] = buffer[name]
        # Which sensor names are we taking the derivative of
        sensorNames = ['dRES1','dRES2','dRES3','dRES4','dRES5','dRES6','dRES7']
        # Calculate the derivative of each sensor
        for name in sensorNames:
            # Calculate the derivative
            sigproc[name] = np.gradient(buffer[name[1:]],buffer['timestamp'])
        # Create a new list of sensor names by combining the old names with the new names
        newNames = []
        for name in header:
            newNames.append(name)
        for name in sensorNames:
            newNames.append(name)
        # Open the analysis file and write the data
        f = open('DATA/LJanalysis.csv','w')
        # Write the header
        for name in newNames:
            if name == newNames[-1]:
                f.write('%s\n'%name)
            else:
                f.write('%s;'%name)
        # Write the data
        #for i in range(len(sigproc['timestamp'])):
        i = -1
        for name in newNames:
            if name == newNames[-1]:
                f.write('%.5f\n'%sigproc[name][i])
            else:
                f.write('%.5f;'%sigproc[name][i])
        f.close()

    # Get the time since the loop started
    ts = time.time()-ts
    # Determine the time to wait
    ts = 1/scanRate-ts
    if ts > 0:
        # Wait for the next scan
        time.sleep(ts)
