
from collections import deque
import time
import csv

# Initialize circular buffer with a fixed size of 1800
circular_buffer = deque(maxlen=1800)

# Read the second row of the file into an array
with open('DATA/LJdata.csv', 'r') as f:
    next(f)  # skip first row
    data = next(f).strip().split(';')

# Initialize variables for averaging
sum_data = [0] * len(data)
num_data = 0
start_time = time.time()

while True:
    # Append the array to the circular buffer
    circular_buffer.append(data)

    # Add the data to the sum for averaging
    for i in range(len(data)):
        sum_data[i] += float(data[i])
    num_data += 1

    # If 10 seconds have passed, calculate the average and print it
    if time.time() - start_time >= 10:
        avg_data = [sum_data[i] / num_data for i in range(len(data))]
        with open('DATA/LJbuffer.csv', mode='a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(avg_data)
        sum_data = [0] * len(data)
        num_data = 0
        start_time = time.time()

    # If the circular buffer is full, remove the oldest element from the buffer
    if len(circular_buffer) == 1800:
        data = circular_buffer.popleft()

    # Wait for 1 second before repeating
    time.sleep(1)
