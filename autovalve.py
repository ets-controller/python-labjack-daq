import os
import time
import numpy as np
import datetime as dt

import RPi.GPIO as GPIO

DATA = 'DATA'
buffName = 'LJanalysis.csv'

analysis = {};results = {}
analysis['overFill'] = 'RES7'
analysis['ident'] = ['dRES1','dRES2']

avgTime = 10*60 # seconds 

buffr = os.path.join(DATA,buffName)

valve = 19 #GPIO BCM pin for relay
status = False # Default valve status 

fillTime = 6*60 # min*s
scanTime = 2
cdTime = 15*60 # minimum time before next fill cycle
ts = [0,0]

closeVolt = 9.8
closedVolt = 9.0
openVolt = -1E-4

waiting = True
filling = False
closing = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(valve,GPIO.OUT)
GPIO.output(valve,status)

STATE = {False:'CLOSED',True:'OPEN'}

def toggleWait():
    time.sleep(1.0)

def toggleValve():
    GPIO.output(valve,False);toggleWait()
    GPIO.output(valve,True);toggleWait()
    GPIO.output(valve,False)

def alarm():
    return 0

if __name__ == '__main__':
    endFill = dt.datetime.utcnow().timestamp()
    printstate = 1
    while True:
        try:
            ts[0] = dt.datetime.utcnow().timestamp()
            try:
                data = np.genfromtxt(buffr,comments='#',delimiter=';',skip_header=1,skip_footer=1,names=True,usecols=np.arange(colspace))
            except:
                time.sleep(1)
                continue
            if waiting:
                if printstate == 1:
                    # waiting for fill cycle
                    printstate = 0
                openCount = 0
                if data['%s'%analysis['overFill']][-1] > closeVolt:
                    # this is weird, the overfill sensor is active before a fill cycle...
                    toggleValve()
                    closeCount = 0
                    waiting = False
                    closing = True
                    printstate = 1
                if dt.datetime.utcnow().timestamp() - endFill > cdTime:
                    for strname in analysis['ident']:
                        if data['%s'%strname][-1] < openVolt:
                            openCount += 1
                            # openCount = %i'%openCount
                    if openCount == len(analysis['ident']):
                        # openCount = all: going to fill cycle
                        GPIO.output(valve,True)
                        waiting = False
                        filling = True
                        printstate = 1
            if filling:
                if printstate == 1:
                    # filling started
                    printstate = 0
                startFill = dt.datetime.utcnow().timestamp()
                closeCount = 0
                if data['%s'%analysis['overFill']][-1] > closeVolt:
                    # overfill detected: close valve
                    toggleValve()
                    filling = False
                    closing = True
                    printstate = 1
                elif (dt.datetime.utcnow().timestamp()-startFill) > fillTime:
                    # fill time exceeded: close valve
                    toggleValve()
                    filling = False
                    closing = True
                    printstate = 1
            if closing:
                if printstate == 1:
                    # closing valve
                    printstate = 0
                endFill = dt.datetime.utcnow().timestamp()
                if dt.datetime.utcnow().timestamp()-endFill > avgTime:
                    toggleValve()
                    closeCount += 1
                    # close time exceeded: close valve
                    endFill = dt.datetime.utcnow().timestamp()
                if closeCount == 5:
                    alarm()
                if data['%s'%analysis['overFill']][-1] < closedVolt:
                    # LN sensor has dropped: the valve is closed
                    closing = False
                    waiting = True
                    printstate = 1
            ts[1] = dt.datetime.utcnow().timestamp()
            procTime = ts[1]-ts[0]
            if (scanTime-procTime) > 0:
                waitTime = np.abs(scanTime-procTime)
                time.sleep(waitTime)
        except:
            continue
