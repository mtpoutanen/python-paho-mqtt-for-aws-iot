#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# use this program to test the AWS IoT certificates received by the author
# to participate to the spectrogram sharing initiative on AWS cloud

# this program will publish test mqtt messages using the AWS IoT hub
# to test this program you have to run first its companion awsiotsub.py
# that will subscribe and show all the messages sent by this program

import paho.mqtt.client as paho
import ssl
import string
import threading
import random
from time import sleep
from random import uniform

connflag = False


def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    print("Connection returned result: " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message

awshost = "data.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "myThingName"
thingName = "myThingName"
caPath = "aws-iot-rootCA.crt"
certPath = "cert.pem"
keyPath = "privkey.pem"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED,
              tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_start()

def randomstring(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def send_temperature():
    while True:
        sleep(0.5)
        if connflag:
            tempreading = uniform(20.0, 25.0)
            mqttc.publish("someId/temperature", tempreading, qos=1)
            print("msg sent: someId/temperature " + "%.2f" % tempreading)
        else:
            print("waiting for connection...")

def send_random_stuff():
    while True:
        sleep(3.0)
        if connflag:
            randstring = randomstring()
            mqttc.publish("someId/otherinfo", randstring, qos=1)
            print("msg sent to someId/otherinfo: %s" % randstring)
        else:
            print("waiting for connection...")

t1 = threading.Thread(target=send_temperature)
t1.start()
t2 = threading.Thread(target=send_random_stuff)
t2.start()

