#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import queue

########################################################################
## Queue for data exchange initialization
########################################################################
exch_queue = queue.Queue()

########################################################################
## MQTT communication logic
########################################################################
MQTT_HOSTNAME = "192.168.0.102" # this must be IP address of computer
MQTT_PORT = 10042               # use port over 10000 !
MQTT_TOPIC = "/sound_data"  

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global exch_queue
    exch_queue.put(msg.payload.decode("utf-8"))
    print(msg.topic+" "+msg.payload.decode("utf-8")) # for debug purpose only

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOSTNAME, MQTT_PORT, 60)
client.loop_start()

########################################################################
## Main loop logic
########################################################################

while True:
    a = 1
    # TODO add some logic
