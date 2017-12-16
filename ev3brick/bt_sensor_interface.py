#!/usr/bin/env python3
import time
import sys
from collections import deque
from bluetooth import *
import ev3dev.ev3 as ev3
import signal, sys
from timeit import default_timer as timer

tmp_bench_full = [] # benchmarking full loop with sending
tmp_bench_pass = [] # benchmarking loop without sending

ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.RED)
ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.RED)

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

########################################################################
## Bluetooth communication logic
########################################################################

BT_ADDR = "C0:EE:FB:27:84:7D"
UUID = "09579b39-da5f-47be-9e59-77ad6793c725"

def bluetooth_setup():

    ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.ORANGE)
    ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.ORANGE)

    # Loop until service is connected
    while(True):
        service_matches = find_service( uuid = UUID, address = BT_ADDR )
        if len(service_matches) == 0:
            print("couldn't find the SampleServer service =(")
        else:
            print("service found...")
            break
        time.sleep(1)

    ev3.Leds.set_color(ev3.Leds.LEFT, ev3.Leds.GREEN)
    ev3.Leds.set_color(ev3.Leds.RIGHT, ev3.Leds.GREEN)

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    print("connecting to \"%s\" on %s" % (name, host))

    # Create the client socket
    sock=BluetoothSocket( RFCOMM )
    sock.connect((host, port))

    return sock

sock = bluetooth_setup()

########################################################################
## Linux signal handler
########################################################################
# This function is called to peacefully
def signal_handler(signal, frame):
    print('Script is stopping due to user request !')
    print('Benchmark full loop: ',(sum(tmp_bench_full)*1.0)/len(tmp_bench_full))
    print('Benchmark full loop: ',(sum(tmp_bench_pass)*1.0)/len(tmp_bench_pass))
    # TODO add disconnect logic
    sys.exit(0)

# Bind to SIGUSR1
signal.signal(signal.SIGUSR1, signal_handler)

########################################################################
## MAIN logic
########################################################################
LAST_NOTE = 0   # last sent value of note (range sensor value)
LAST_BTN = 0    # last sent value of button (play note / don't play)
LAST_CLC = 0    # last sent value of clucth (octave modifier)

# function checks if any value has changed for more than threshold value
def check_any_different(diff_note, diff_btn, diff_clc, threshold):
    if diff_btn != 0:
        return True
    if diff_note > threshold:
        return True
    if diff_clc > threshold:
        return True
    return False

# loop forever
while True:
    time_start = timer()

    new_note = FastRead(irSensorValueRaw)
    new_btn  = FastRead(touchSensorValueRaw)
    new_clc  = FastRead(motorMediumValueRaw)

    # check for change in data
    if check_any_different(abs(LAST_NOTE-new_note), abs(LAST_BTN-new_btn), abs(LAST_CLC-new_clc), 2):
        LAST_NOTE = new_note
        LAST_BTN = new_btn
        LAST_CLC = new_clc

        try:
            sock.send(str(new_note)+";"+str(new_btn)+";"+str(new_clc))
        except:
            sock = bluetooth_setup()

        time_end = timer()

        if(len(tmp_bench_full) > 9):
            tmp_bench_full.pop()
        tmp_bench_full.append(time_end - time_start)

    # no change - currently only for benchmarking
    else:
        time_end = timer()

        if(len(tmp_bench_pass) > 9):
            tmp_bench_pass.pop()
        tmp_bench_pass.append(time_end - time_start)

    # throttle the loop
    time.sleep(0.01)
    
