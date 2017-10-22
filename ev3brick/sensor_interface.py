#!/usr/bin/env python3
import time
import sys
from collections import deque
import ev3dev.ev3 as ev3

########################################################################
## Fast file I/O functions (faster than API interface)
########################################################################

# Function for fast reading from sensor files
def FastRead(infile):
    infile.seek(0)    
    return(int(infile.read().decode().strip()))

# Function for fast writing to motor files    
def FastWrite(outfile,value):
    outfile.truncate(0)
    outfile.write(str(int(value)))
    outfile.flush()

########################################################################
## EV3 Hardware setup
########################################################################

# Touch Sensor setup
touchSensor         = ev3.TouchSensor()
touchSensorValueRaw = open(touchSensor._path + "/value0", "rb")

# IR Buttons setup
irSensor          = ev3.InfraredSensor()
irSensor.mode     = irSensor.MODE_IR_PROX
irSensorValueRaw  = open(irSensor._path + "/value0", "rb") 

# Configure the motors
motorMedium         = ev3.MediumMotor('outD')
motorMediumValueRaw = open(motorMedium ._path + "/position", "rb")