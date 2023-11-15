import os
import time
import csv
import numpy as np
from readLJ import buffer_output

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

# Define scanRate and avgTime
scanRate, avgTime, bufferSize = buffer_output()[2], 10, 30 # Seconds
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
    # If there are more than 30 minutes worth of data points in the buffer, delete the oldest data point
    # Check how many rows are in the buffer file, excluding the header
    with open('DATA/LJbuffer.csv','r') as g:
        reader = csv.reader(g, delimiter=';')
        row_count = sum(1 for row in reader)-1
        g.close()
    # Open the buffer file and write the data
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

    # Get the time since the loop started
    ts = time.time()-ts
    # Determine the time to wait
    ts = 1/scanRate-ts
    if ts > 0:
        # Wait for the next scan
        time.sleep(ts)
