#!/usr/bin/bin/python
import sys
import Adafruit_DHT
import time
import datetime

while True:
    print(datetime.datetime.now())
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    print 'Temp: {0:0.1f} C Humidity: {1:0.1f} %\n'.format(temperature, humidity)
    time.sleep(300)
