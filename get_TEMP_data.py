import time, threading
import paho.mqtt.client as mqtt

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

MQTT_ADDRESS = '192.168.178.25'
MQTT_USER = 'finbar'
MQTT_PASSWORD = 'finbar'
MQTT_TOPIC = 'home/+/+'

myChannel = "Homesafe"
sensorList = ["buzzer"]
data = {}


pnconfig = PNConfiguration()
pnconfig.cipher_key = 'myCipherKey'
pnconfig.auth_key = 'Homesafe-Finbar-Raspberry-Pi'
pnconfig.subscribe_key = 'sub-c-12924b4c-2f48-11eb-9713-12bae088af96'
pnconfig.publish_key = 'pub-c-4c71c151-b075-498f-bfbc-c6f3221ed3b6'
pnconfig.uuid = '62d358a1-ee39-4aba-8950-2677d2dd5bcd'#'8f255df0-3657-11eb-adc1-0242ac120002'
pubnub = PubNub(pnconfig)

def publish(custom_channel, msg):
    pubnub.publish().channel(custom_channel).message(msg).pn_async(my_publish_callback)

def my_publish_callback(envelope, status):
     # Check whether request successfully completed or not
     if not status.is_error():
         pass  # Message successfully published to specified channel.
     else:
         pass  # Handle message publish error. Check 'category' property to find out possible issue
         # because of which request did fail.
         # Request can be resent using: [status retry];


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

def status(self, pubnub, status):
    if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
        pass  # This event happens when radio / connectivity is lost

    elif status.category == PNStatusCategory.PNConnectedCategory:
        # Connect event. You can do stuff like publish, and know you'll get it.
        # Or just use the connected event to confirm you are subscribed for
        # UI / internal notifications, etc
        pubnub.publish().channel(myChannel).message('Connected to PubNub').pn_async(my_publish_callback)
    elif status.category == PNStatusCategory.PNReconnectedCategory:
        pass
    # Happens as part of our regular operation. This event happens when
    # radio / connectivity is lost, then regained.
    elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
        pass
        # Handle message decryption error. Probably client configured to
        # encrypt messages and on live data feed it received plain text.

def message(self, pubnub, message):
    # Handle new message stored in message.message
    try:
        print(message.message)
        msg = message.message
        key = list(msg.keys())
        if key[0] == "event":       #{"event" : {"sensor_name" : True}}
            self.handleEvent(msg)
    except Exception as e:
        print("Received: ", message.message)
        print(e)
        pass


def handleEvent(self, msg):
    global data
    eventData = msg["event"]
    key = list(eventData.keys())
    if key[0] in sensorList:
        if eventData[key[0]] is True:
            data["alarm"] = True
        elif eventData[key[0]] is False:
            data["alarm"] = False

# MQTT

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server. """
    print('Connected with the result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """ The callback for when a PUBLISH message is received from the server. """
    print('\n' + msg.topic + '\t' + str(msg.payload))
    temp, hum = str(msg.payload).split(",")
    publish(myChannel, {"atmos":{"tempC":float(temp),"hum":float(hum)}})


def temp_sensor():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == "__main__":
    tempThread = threading.Thread(target=temp_sensor)
    tempThread.start()
#    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(myChannel).execute()
