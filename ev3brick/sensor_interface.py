#!/usr/bin/env python3
import time
import sys
from collections import deque
import ev3dev.ev3 as ev3
import paho.mqtt.client as mqtt
import signal, sys
from timeit import default_timer as timer

tmp_bench_full = [] # benchmarking full loop with sending
tmp_bench_pass = [] # benchmarking loop without sending

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
## MQTT communication logic
########################################################################
MQTT_HOSTNAME = "192.168.0.102" # this must be IP address of computer
MQTT_PORT = 10042           # use port over 10000 !
MQTT_TOPIC = "/sound_data"  

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)

client = mqtt.Client()
client.on_connect = on_connect
client.connect(MQTT_HOSTNAME, MQTT_PORT, 60)

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

        client.publish(MQTT_TOPIC, str(new_note)+";"+str(new_btn)+";"+str(new_clc));
        client.loop_write()

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
    