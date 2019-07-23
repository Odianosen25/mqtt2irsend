#!/usr/bin/python3

from py_irsend import irsend
import paho.mqtt.client as mqtt
import json
import sys
import os
import yaml

"""
Parse and load the configuration file to get MQTT credentials
"""

config={}
DEVICE=None
ADDRESS=None

def parseConfig():
    global config
    global DEVICE
    global ADDRESS

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(dir_path, "mqtt2irsendconfig.yaml")
    with open(config_file, 'r') as stream:
        try:
            config = yaml.load(stream, Loader=yaml.SafeLoader)

            if "DEVICE" in config:
                DEVICE = config["DEVICE"]

            if "ADDRESS" in config:
                ADDRESS = config["ADDRESS"]

        except yaml.YAMLError as exc:
            print(exc)
            print("Unable to parse configuration file at {}".format(config_file))
            sys.exit(1)

"""
Define a state object to preserve an internal AC state so that we can have more complex decisions later
"""

def on_connect(client, userdata, flags, rc):
    global config

    """
    The callback for when the client receives a CONNACK response from the MQTT server.
    """
    print("Connected with result code "+str(rc))
    sys.stdout.flush()

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    topic = config["MQTT_TOPIC"]
    (result, mid) = client.subscribe(topic)
    
    if result == 0:
        print("Subscription to {} was Sucessful".format(topic))
    else:    
        print("Subscription to {} was Unsucessful, with result {}".format(topic, result))
        
    sys.stdout.flush()

def on_message(client, userdata, msg):
    global config
    global DEVICE
    global ADDRESS

    """
    The callback for when a PUBLISH message is received from the MQTT server.
    """
    print("Received command:"+msg.topic+" "+str(msg.payload))
    sys.stdout.flush()

    """
    Handle IR Commands
    """

    payload = json.loads(msg.payload.decode())

    if "device" in payload:
        DEVICE = payload["device"]
    
    if "address" in payload:
        ADDRESS = payload["address"]
    
    command = payload["command"]
    remote = payload["remote"]
    codes = payload["codes"]
    count = payload.get("count", None) 
    
    if command == "send_once":
        if isinstance(codes, str):
            codes = [codes]

        irsend.send_once(remote, codes, device=DEVICE, address=ADDRESS, count=count)
    
    else:
        if hasattr(irsend, command):
            func = getattr(irsend, command)
            func(remote, codes, device=DEVICE, address=ADDRESS)

"""
Initialize the MQTT object and connect to the server, looping forever waiting for messages
"""
parseConfig()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print ('Starting mqtt2irsend')
sys.stdout.flush()

BROKER = config.get('MQTT_BROKER')
PORT = config.get('MQTT_PORT', 1883)
USERNAME = config.get('MQTT_USERNAME', None)
PASSWORD = config.get('MQTT_PASSWORD', None)
CA_CERT = config.get('MQTT_CA_CERT', "")

if USERNAME and PASSWORD:
    client.username_pw_set(username=USERNAME, password=PASSWORD)

client.connect_async(BROKER, PORT, 60)
client.loop_start()

#client.connect(BROKER, PORT, 60)
#client.loop_forever()
