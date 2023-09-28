import RPi.GPIO as GPIO

valve = 15 #GPIO BCM pin for relay
status = False # Default valve status 

GPIO.setmode(GPIO.BCM)
GPIO.setup(valve,GPIO.OUT)
GPIO.output(valve,status)

STATE = {False:'CLOSED',True:'OPEN'}

while True:
    print('\nThe RELAY is %s'%STATE[status])
    print('Return "0" to close the relay or "1" to open it.')
    new_status = input('Would you like to toggle the relay? : ')
    if new_status == '0':
        status = False
    elif new_status == '1':
        status = True
    else:
        print('Command not recognized, relay closed')
        status = False
    GPIO.output(valve,status)
