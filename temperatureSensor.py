import RPi.GPIO as GPIO
import time, threading

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import Adafruit_DHT

PIR_pin = 23
Buzzer_pin = 24
dht11_pin = 16


myChannel = "Homesafe"
sensorList = ["buzzer"]
data = {}



pnconfig = PNConfiguration()
pnconfig.cipher_key = 'myCipherKey'
pnconfig.auth_key = 'Homesafe-Roisin-Raspberry-Pi'
pnconfig.subscribe_key = 'sub-c-12924b4c-2f48-11eb-9713-12bae088af96'
pnconfig.publish_key = 'pub-c-4c71c151-b075-498f-bfbc-c6f3221ed3b6'
pnconfig.uuid = 'c26f2970-3fc1-11eb-b378-0242ac130002'
pubnub = PubNub(pnconfig)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(Buzzer_pin, GPIO.OUT)

def beep(repeat):
    for i in range(0, repeat):
        for pulse in range(60):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.001)
        time.sleep(0.02)


def motionDetection():
    data["alarm"] = False
    print("Sensors started")
    trigger = False
    while True:
        if GPIO.input(PIR_pin):
            print("Motion detected")
            beep(4)
            trigger = True
            publish(myChannel, {"motion" : "Yes"})
            time.sleep(1)
        elif trigger:
            publish(myChannel, {"motion" : "No"})

        if data["alarm"]:
            beep(2)

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

def read_dht11():
    while(True):
        time.sleep(2) #sleep time is used to measure temp every 2 secs
        hum, tempC = Adafruit_DHT.read_retry(22, dht11_pin)
        print(hum)
        print(tempC)
        publish(myChannel, {"atmos":{"tempC":round(tempC,1), "hum":(int)(hum)}})



if __name__ == "__main__":
    pubnub.add_listener(MySubscribeCallback())
    pubnub.subscribe().channels(myChannel).execute()
    time.sleep(3) 

    dhtThread = threading.Thread(target=read_dht11)
    dhtThread.start()

