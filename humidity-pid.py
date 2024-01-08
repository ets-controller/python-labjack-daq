import time
import serial
import RPi.GPIO as GPIO

def setupRelay(pin=19, status=False):
    """
    Sets up the relay for controlling the valve.

    This function initializes the GPIO mode and sets the specified pin as an output.

    Parameters:
    pin (int): The GPIO BCM pin number for the relay. Default is 19.
    status (bool): The initial status of the valve. Default is False.

    Returns:
    None
    """
    # Set the GPIO mode
    GPIO.setmode(GPIO.BCM)
    # Set the pin as an output
    GPIO.setup(pin, status)
    return pin, status

def readSerial(port='/dev/ttyUSB0', baudrate=9600, value=2):
    """
    Connects to a serial port and reads the serial output.

    This function establishes a connection to the specified serial port and reads the serial output.

    Parameters:
    port (str): The serial port to connect to. Default is '/dev/ttyUSB0'.
    baudrate (int): The baud rate for the serial communication. Default is 9600.
    value (int): The index of the value to extract from the serial output. Default is 2.

    Returns:
    float: The value extracted from the serial output.

    Raises:
    SerialException: If there is an error while establishing the serial connection.
    ValueError: If the value index is out of range or the extracted value cannot be converted to float.
    """
    ser = serial.Serial(port, baudrate)
    humidity = float(ser.readline().decode('utf-8').split(',')[value])
    ser.close()
    return humidity

def startLoop(pin, read_frequency=1, average_size=60, buffer_size=100):
    """
    Starts the main loop.

    This function starts the main loop for the program.

    Parameters:
    - pin (int): The pin number to output the status.
    - read_frequency (float): The frequency at which to read the humidity sensor in Hertz.
    - average_size (int): The duration in seconds over which to calculate the average humidity.
    - buffer_size (int): The number of entries to store in the buffer.

    Returns:
    None
    """
    average = []
    buffer = []
    T = 1/read_frequency
    try:
        while True:
            t0 = time.time()
            humidity = readSerial()
            average.append((t0, humidity))
            
            if len(average) > average_size:
                avg_t0 = sum([entry[0] for entry in average]) / len(average)
                avg_humidity = sum([entry[1] for entry in average]) / len(average)
                buffer.append((avg_t0, avg_humidity))

                status = feedback(buffer)
                GPIO.output(pin,status)
                
                if len(buffer) > buffer_size:
                    buffer.pop(0)
                
                average = []
            
            t1 = time.time()
            if t1 - t0 < T:
                wait = T - (t1 - t0)
                time.sleep(wait)
    except KeyboardInterrupt:
        # Handle keyboard interrupt
        GPIO.cleanup()

def feedback(buffer, setpoint=10, Kp=1, Ki=1, Kd=1):
    """
    Calculates the PID output.

    This function calculates the PID output based on the current humidity and the setpoint.

    Parameters:
    buffer (list): The buffer of humidity values.
    setpoint (float): The desired humidity value.
    Kp (float): The proportional gain. Default is 1.
    Ki (float): The integral gain. Default is 1.
    Kd (float): The derivative gain. Default is 1.

    Returns:
    bool: The status of the valve.
    """
    # Initialize the output
    output = False

    # Calculate the error
    error = - (setpoint - buffer[-1][1])
    # Calculate the integral
    integral = sum([(setpoint-entry[1]) for entry in buffer])
    # Calculate the derivative
    derivative = (buffer[-1][1] - buffer[-2][1]) / (buffer[-1][0] - buffer[-2][0])

    # Calculate the output
    if error > 0:
        output = True

    # Return the status
    return output

if __name__ == '__main__':
    # Setup the relay
    pin, status = setupRelay()
    startLoop(pin)





    



