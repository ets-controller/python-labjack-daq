import RPi.GPIO as GPIO

valve = 15 #GPIO BCM pin for relay
status = False # Default valve status 

GPIO.setmode(GPIO.BCM)
GPIO.setup(valve,GPIO.OUT)
GPIO.output(valve,status)

STATE = {False:'ACTIVE',True:'INACTIVE'}

while True:
    print('\nThe FRG is %s'%STATE[status])
    print('Return "0" to set the FRG to ACTIVE or "1" to INACTIVE.')
    new_status = input('Would you like to toggle the gauge status? : ')
    if new_status == '0':
        status = False
    elif new_status == '1':
        status = True
    else:
        print('Command not recognized, FRG is active')
        status = False
    GPIO.output(valve,status)
