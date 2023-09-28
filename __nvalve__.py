import RPi.GPIO as GPIO

bvalve = 18 #BCM pin for relay
dvalve = 23
bstatus = True # Default valve status 
dstatus = True # Default valve status 

GPIO.setmode(GPIO.BCM)
GPIO.setup(bvalve,GPIO.OUT)
GPIO.setup(dvalve,GPIO.OUT)
GPIO.output(bvalve,bstatus)
GPIO.output(dvalve,dstatus)

STATE = {False:'OPEN',True:'CLOSED'}

while True:
    print('\nEnter "bottle" to access the bottle nitrogen;\nEnter "dewar" to access the boil-off nitrogen')
    if not 'type_status' in globals():
        type_status = input('Which nitrogen valve would you like to access?')
    if not type_status in ['bottle','dewar']:
        type_status = input('Which nitrogen valve would you like to access?')
    while type_status == 'bottle':
        print('\nEnter "bottle" to access the bottle nitrogen;\nEnter "dewar" to access the boil-off nitrogen')
        print('\nThe BOTTLE VALVE is %s'%STATE[bstatus])
        print('Return "0" to close the bottle valve or "1" to open it.')
        new_status = input('Would you like to toggle the valve? : ')
        if new_status == '0':
            bstatus = True
        elif new_status == '1':
            bstatus = False
        elif new_status == 'dewar':
            type_status = 'dewar'
            bstatus = True
        else:
            print('Command not recognized, valve closing')
            bstatus = True
        GPIO.output(bvalve,bstatus)       
    while type_status == 'dewar':
        print('\nEnter "bottle" to access the bottle nitrogen;\nEnter "dewar" to access the boil-off nitrogen')
        print('\nThe BOIL-OFF VALVE is %s'%STATE[dstatus])
        print('Return "0" to close the boil-off valve or "1" to open it.')
        new_status = input('Would you like to toggle the valve? : ')
        if new_status == '0':
            dstatus = True
        elif new_status == '1':
            dstatus = False
        elif new_status == 'bottle':
            type_status = 'bottle'
            dstatus = True
        else:
            print('Command not recognized, valve closing')
            dstatus = True
        GPIO.output(dvalve,dstatus)       
