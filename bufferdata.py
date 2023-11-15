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

# Define scanRate and avgTime
scanRate, avgTime = buffer_output()[3], buffer_output()[4]