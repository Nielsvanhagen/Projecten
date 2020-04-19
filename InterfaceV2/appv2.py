#import library
from flask import Flask, Response, render_template
import json
 
from datetime import datetime
from datetime import timedelta  

#define open browser
import webbrowser
from threading import Timer

#import for API (weather)
import requests

import time

#ultra sonic
#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

channel = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

api_address='http://api.openweathermap.org/data/2.5/weather?APPID=a62699263199cff6bc9755b6529c08db&q='
city = "Rotterdam"
url = api_address + city

#define app
app = Flask(__name__)

def callback(channel):
        if GPIO.input(channel):
                print "Sound Detected!"
        else:
                print "Sound Detected!"

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def addSecs(tm, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(seconds=secs)
    return fulldate.time()

def temperature():
    json_temp = requests.get(url).json()
    return round(json_temp['main']['temp'] - 273.15)

def current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-data')
def get_data():
    def generate_random_data():
        current_time_30 = datetime.now()
        while True:
            temperature_var = temperature()

            current_time_var = current_time()

            dist = distance()

            print(temperature_var)
            print(dist)
            if(current_time_30 < datetime.now()):
                detect = False
                
            if(dist < 50):          
                current_time_30 = datetime.now() + timedelta(seconds=30)
                print(current_time_30)
                detect = True
                
            if(detect):    
                print("* Scene 1 activating")
                top_text = "Hallo daar, kom eens dichter bij!"
                scene = 1
                json_data = json.dumps(
                    {'top_text': top_text,
                     'scene': scene})
                yield f"data:{json_data}\n\n"
        
            if(detect == False):
                print("* Scene 2 activating")
                scene = 2
                top_text = "Het is momenteel " + str(temperature_var) + "graden"
                json_data = json.dumps(
                    {'top_text': top_text,
                     'scene': scene})
                yield f"data:{json_data}\n\n"
                    

            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    #Timer(1, open_browser).start()
    app.run(debug=True, threaded=True)
