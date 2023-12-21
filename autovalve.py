import os
import time
import numpy as np
import datetime as dt

import RPi.GPIO as GPIO

DATA = 'DATA'
buffName = 'LJanalysis.csv'
strmName = 'LJdata.csv'

closeSensor = ['RES7','RES1']
openSensor = ['dRES1','dRES2']

avgTime = 10*60 # seconds 

buffr = os.path.join(DATA,buffName)
strmr = os.path.join(DATA,strmName)

valve = 19 #GPIO BCM pin for relay
status = False # Default valve status 

fillTime = 6*60 # min*s
scanTime = 2
cdTime = 15*60 # minimum time before next fill cycle
ts = [0,0]

closeVolt = 9.8
closedVolt = 9.0
openVolt = -1E-4
fullVolt = 9.45

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

def loadData(buffr,strmr):
    buff = np.genfromtxt(buffr,comments='#',delimiter=';',names=True)
    strm = np.genfromtxt(strmr,comments='#',delimiter=';',names=True)
    return buff,strm

if __name__ == '__main__':
    endFill = dt.datetime.utcnow().timestamp()
    while True:
        try:
            ts[0] = dt.datetime.utcnow().timestamp()
            try:
                buff,strm = loadData(buffr,strmr)
                overfill = strm['%s'%closeSensor[0]][-1]
                fill = strm['%s'%closeSensor[1]][-1]
            except:
                print('cannot load data')
                time.sleep(1)
                continue

            print('Overfill: %f'%overfill)
            print('Fill: %f'%fill)
            
            if waiting:
                openCount = 0
                if overfill > closeVolt:
                    # this is weird, the overfill sensor is active before a fill cycle...
                    toggleValve()
                    closeCount = 0
                    waiting = False
                    closing = True
                elif fill > fullVolt:
                    # this is weird, the overfill sensor is active before a fill cycle...
                    toggleValve()
                    closeCount = 0
                    waiting = False
                    closing = True
                elif dt.datetime.utcnow().timestamp() - endFill > cdTime:
                    for strname in openSensor:
                        if data['%s'%strname][-1] < openVolt:
                            openCount += 1
                            # openCount = %i'%openCount
                    if openCount == len(openSensor):
                        # openCount = all: going to fill cycle
                        GPIO.output(valve,True)
                        waiting = False
                        filling = True
            if filling:
                startFill = dt.datetime.utcnow().timestamp()
                closeCount = 0
                if overfill > closeVolt:
                    # overfill detected: close valve
                    toggleValve()
                    filling = False
                    closing = True
                elif fill > fullVolt:
                    # Fill detected: close valve
                    toggleValve()
                    filling = False
                    closing = True
                elif (dt.datetime.utcnow().timestamp()-startFill) > fillTime:
                    # fill time exceeded: close valve
                    toggleValve()
                    filling = False
                    closing = True
            if closing:
                endFill = dt.datetime.utcnow().timestamp()
                if dt.datetime.utcnow().timestamp()-endFill > avgTime:
                    toggleValve()
                    closeCount += 1
                    # close time exceeded: close valve
                    endFill = dt.datetime.utcnow().timestamp()
                if closeCount == 5:
                    alarm()
                if overfill < closedVolt:
                    # LN sensor has dropped: the valve is closed
                    closing = False
                    waiting = True

            ts[1] = dt.datetime.utcnow().timestamp()
            procTime = ts[1]-ts[0]
            if (scanTime-procTime) > 0:
                waitTime = np.abs(scanTime-procTime)
                time.sleep(waitTime)
        except KeyboardInterrupt:
            GPIO.cleanup()
            break
