
from collections import deque
import time

# Initialize circular buffer with a fixed size of 1800
circular_buffer = deque(maxlen=1800)

# Read the second row of the file into an array
with open('DATA/LJdata.csv', 'r') as f:
    next(f)  # skip first row
    data = next(f).strip().split(';')

while True:
    # Append the array to the circular buffer
    circular_buffer.append(data)

    # If the circular buffer is full, remove the oldest element from the buffer
    if len(circular_buffer) == 1800:
        circular_buffer.popleft()

    # Wait for 1 second before repeating
    time.sleep(1)
