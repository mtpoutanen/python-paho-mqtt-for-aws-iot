#!/usr/bin/python

# this source is part of my Hackster.io project:
# https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# use this program to test the AWS IoT certificates received by the author
# to participate to the spectrogram sharing initiative on AWS cloud

# this program will publish test mqtt messages using the AWS IoT hub
# to test this program you have to run first its companion awsiotsub.py
# that will subscribe and show all the messages sent by this program

import sys
import json
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


def send_report():
    is_sent = False
    while not is_sent:
        sleep(1.0)
        if connflag:
            data_dict = {
                'ID': '000000000000',
                'Temperature': 24.1,
                'SetPoint': 25.5,
                'ValvePosition': 50,
                'BatteryLevel': 75.4,
                'RSSI': -22.4
            }

            data_json = json.dumps(data_dict)
            mqttc.publish("staging/report", data_json, qos=1)
            print("msg sent to staging/report: %s" % data_json)
            # Need to sleep here for a bit so that the script won't exit before the message has been sent
            # sleep(3.0)
            # is_sent = True
        else:
            print("waiting for connection...")


def send_registration():
    is_sent = False
    while not is_sent:
        sleep(1.0)
        if connflag:
            data_dict = {
                'MACaddress': '123412341234',
                'IPaddress': '123.123.23.34'
            }
            data_json = json.dumps(data_dict)
            mqttc.publish("staging/register", data_json, qos=1)
            print("msg sent to staging/register: %s" % data_json)
            # Need to sleep here for a bit so that the script won't exit before the message has been sent
            # sleep(3.0)
            # is_sent = True
        else:
            print("waiting for connection...")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'register':
        send_registration()
    elif len(sys.argv) > 1 and sys.argv[1] == 'report':
        send_report()
    else:
        t1 = threading.Thread(target=send_temperature)
        t1.start()
        t2 = threading.Thread(target=send_random_stuff)
        t2.start()
