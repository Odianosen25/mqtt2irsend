# mqtt2irsend
This is a simple code written to run on the same Pi running Kodi. 
It is intended to be used as a MQTT to IR controller, making use of a Raspberry Pi.
I have always wanted to use a single Pi to do several things, so instead of having a standalone IR device, 
the same Pi can be used for IR control of IR devices. For this system, I make use of the OSMC Kodi instance

To install the system, run the following code

```
$ sudo apt-get update
$ sudo apt-get install python3-pip
$ sudo apt-get install python3-venv

$ python3 -m venv mqtt2irsend
$ cd mqtt2irsend
/mqtt2irsend$ git clone https://github.com/Odianosen25/mqtt2irsend.git
/mqtt2irsend$ cd
$ source mqtt2irsend/bin/activate

$ cd mqtt2irsend/mqtt2irsend
/mqtt2irsend/mqtt2irsend$ pip3 install -r requirements.txt
/mqtt2irsend/mqtt2irsend$ nano mqtt2irsendconfig.yaml

#modify "mqtt2irsendconfig.yaml" with right parameters

/mqtt2irsend/mqtt2irsend$ deactivate

/mqtt2irsend/mqtt2irsend$ sudo cp mqtt2irsend.service /etc/systemd/system/mqtt2irsend.service

#modify "my-remote.conf" and add your own Lirc codes

/mqtt2irsend/mqtt2irsend$ sudo cp my-remote.conf /etc/lirc/my-remote.conf

#modify the service file and needed with right parameters if needed

$ sudo systemctl daemon-reload

$ sudo systemctl enable mqtt2irsend.service
```

Modify the `mqtt2irsendconfig.yaml` file, as that is used to connect to the MQTT broker. 

In the config file, the `DEVICE` should be set to the device used to control the `lirc` interface in Kodi.

Sample code is as follows:

if using Home Assistant, the following can be used in the scipt:

```
lr_tv_power_on:
  alias: 'Living Room TV Power On'
  sequence:
    service: mqtt.publish
    data:
      topic: ir/kodi/remote/living_room
      payload: "{\"command\":\"send_once\", \"remote\":\"LG_TV\", \"codes\":\"POWER_ON\"}"
```

if using AppDaemon, the following can be used in the function

```
import mqttapi as mqtt
import json

class IRApp(mqtt.Mqtt):
 
    def initialize(self):
      data = {"command" : "send_once", "remote" : "LG_TV", "codes" : "POWER_ON"}
      self.mqtt_publish("ir/kodi/remote/living_room", json.dumps(data))
```

To send multiple IR codes at once, within the same remote, `codes` could be a list of the codes

If running this script on a Pi running a Kodi instance, ensure the remote is activated via the Kodi instance.
