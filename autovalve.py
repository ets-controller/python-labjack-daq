import os
import time
import numpy as np
import datetime as dt

import RPi.GPIO as GPIO

def toggleWait():
    time.sleep(1.0)

def toggleValve():
    GPIO.output(valve,False);toggleWait()

def alarm():
    return 0

def loadData(buffr,strmr):
    buff = np.genfromtxt(buffr,comments='#',delimiter=';',names=True)
    strm = np.genfromtxt(strmr,comments='#',delimiter=';',names=True)
    return buff,strm

if __name__ == '__main__':
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

    fillTime = 10*60 # min*s
    scanTime = 1 # s
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
    endFill = dt.datetime.utcnow().timestamp()
    while True:
        try:
            ts[0] = dt.datetime.utcnow().timestamp()
            try:
                buff,strm = loadData(buffr,strmr)
                #print(buff,strm)
                overfill = strm['%s'%closeSensor[0]]
                fill = strm['%s'%closeSensor[1]]
            except:
                print('cannot load data')
                time.sleep(1)
                continue

            print('Overfill if 9.8 < %f'%overfill)
            print('Full if  9.45 < %f'%fill)
            
            if waiting:
                print('Waiting for fill cycle')
                openCount = 0
                if overfill > closeVolt:
                    # this is weird, the overfill sensor is active before a fill cycle...
                    toggleValve()
                    closeCount = 0
                    waiting = False
                    closing = True
                if fill > fullVolt:
                    # this is weird, the overfill sensor is active before a fill cycle...
                    toggleValve()
                    closeCount = 0
                    waiting = False
                    closing = True
                elif dt.datetime.utcnow().timestamp() - endFill > cdTime:
                    for strname in openSensor:
                        if buff['%s'%strname][-1] < openVolt:
                            openCount += 1
                            # openCount = %i'%openCount
                    if openCount == len(openSensor):
                        # openCount = all: going to fill cycle
                        GPIO.output(valve,True)
                        waiting = False
                        filling = True
            if filling:
                print('Filling')
                startFill = dt.datetime.utcnow().timestamp()
                closeCount = 0
                if overfill > closeVolt:
                    # overfill detected: close valve
                    toggleValve()
                    filling = False
                    closing = True
                if fill > fullVolt:
                    # Fill detected: close valve
                    toggleValve()
                    filling = False
                    closing = True
                if (dt.datetime.utcnow().timestamp()-startFill) > fillTime:
                    # fill time exceeded: close valve
                    toggleValve()
                    filling = False
                    closing = True
            if closing:
                print('Closing')
                endFill = dt.datetime.utcnow().timestamp()
                if dt.datetime.utcnow().timestamp()-endFill > avgTime:
                    toggleValve()
                    closeCount += 1
                    # close time exceeded: close valve
                    endFill = dt.datetime.utcnow().timestamp()
                if closeCount == 5:
                    toggleValve()
                    alarm()
                if overfill < closedVolt:
                    # Ssensor value has dropped: the valve is closed
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
