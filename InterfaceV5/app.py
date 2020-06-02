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


delayt = .1 
value = 0 # this variable will be used to store the ldr value
ldr = 4 #ldr is connected with pin number 7
led = 11 #led is connected with pin number 11
GPIO.setup(led, GPIO.OUT) # as led is an output device so that’s why we set it to output.
GPIO.output(led, False) # keep led off by default

ranCount = 0

def rc_time (ldr):
    count = 0
 
    #Output on the pin for
    GPIO.setup(ldr, GPIO.OUT)
    GPIO.output(ldr, False)
    time.sleep(delayt)
 
    #Change the pin back to input
    GPIO.setup(ldr, GPIO.IN)
 
    #Count until the pin goes high
    while (GPIO.input(ldr) == 0):
        count += 1
 
    return count

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

def windSpeed():
    json_wspeed = requests.get(url).json()
    return round(json_wspeed['wind']['speed'] * 3.6)

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
        current_time_20 = datetime.now()
        current_time_40 = datetime.now()
        global ranCount
        while True:
            temperature_var = temperature()
            windSpeed_var = windSpeed()
            
            current_time_var = current_time()
            dist = distance()
            value = rc_time(ldr)
            
            now = datetime.now()

            digiTime = now.strftime("%H:%M")
            
            noData = False
            
            
            print("Wind speed: " + str(windSpeed_var))
            
            print("Temp: " + str(temperature_var))
            
            print("Dist: " + str(dist))
            
            print("Ldr Value:" + str(value))
            
            #Sound sensor
            if(current_time_20 < datetime.now()):
                soundOn = False
            if (GPIO.input(27) == 0):
                current_time_20 = datetime.now() + timedelta(seconds=5)
                soundOn = True
                print("* Scene 2 activating")
                top_text = "Doe is iets stiller!"
                scene = 2
                json_data = json.dumps(
                 {'top_text': top_text,
                  'scene': scene})
                yield f"data:{json_data}\n\n"
                
            #Ultra sonic
            if(current_time_30 < datetime.now()):
                detect = False
                
            if(dist < 50):          
                current_time_30 = datetime.now() + timedelta(seconds=5)
                detect = True
                print("* Scene 1 activating")
                top_text = "HE jij daar!"
                scene = 1
                json_data = json.dumps(
                 {'top_text': top_text,
                  'scene': scene})
                yield f"data:{json_data}\n\n"
                
            #Sound sensor
            if(current_time_40 < datetime.now()):
                LDROn = False
                
            if (value > 2000):
                current_time_40 = datetime.now() + timedelta(seconds=5)
                LDROn = True
                print("* Scene 3 activating")
                top_text = "Doe het licht eens aan!"
                scene = 3
                json_data = json.dumps(
                 {'top_text': top_text,
                  'scene': scene})
                yield f"data:{json_data}\n\n"    
                
            print(detect)
            print(soundOn)
            print(LDROn)
                
            if((detect == False) & (soundOn == False) &(LDROn == False)):
                noData = True
            else:
                noData = False
                
            print(noData)

            #Loop all scene
            if(noData):
                print("test")
                active = True
                if((ranCount == 0) and (active == True)):
                    if(temperature_var < 10):
                        print("* Scene 106 activating")
                        scene = 106
                        top_text = "Vind jij "+str(temperature_var)+"℃ ook zo koud?"
                        json_data = json.dumps(
                            {'top_text': top_text,
                            'scene': scene})
                        yield f"data:{json_data}\n\n"
                        time.sleep(5)
                        ranCount += 1
                        active = False 
                    else:
                        print("* Scene 101 activating")
                        scene = 101
                        top_text = "Het is momenteel "+str(temperature_var)+"℃"
                        json_data = json.dumps(
                            {'top_text': top_text,
                            'scene': scene})
                        yield f"data:{json_data}\n\n"
                        time.sleep(5)
                        ranCount += 1
                        active = False         
            
                if((ranCount == 1) and (active == True)):
                        print("* Scene 102 activating")
                        scene = 102
                        top_text = "Alle muziek al gehad?"
                        json_data = json.dumps(
                            {'top_text': top_text,
                            'scene': scene})
                        yield f"data:{json_data}\n\n"
                        time.sleep(5)
                        ranCount += 1
                        active = False
                        
                    
                if((ranCount == 2) and (active == True)):
                        print("* Scene 103 activating")
                        scene = 103
                        top_text = "Kapper"
                        json_data = json.dumps(
                            {'top_text': top_text,
                            'scene': scene})
                        yield f"data:{json_data}\n\n"
                        time.sleep(5)
                        ranCount += 1
                        active = False
                        
                if((ranCount == 3) and (active == True)):
                        print("* Scene 104 activating")
                        scene = 104
                        top_text = "Moeite met opstaan?"
                        json_data = json.dumps(
                            {'top_text': top_text,
                            'scene': scene,
                            'digital_time': digiTime})
                        yield f"data:{json_data}\n\n"
                        time.sleep(5)
                        ranCount += 1
                        active = False
                        
                if((ranCount == 4) and (active == True)):
                    if(windSpeed_var > 8):
                        print("* Scene 107 activating")
                        scene = 107
                        top_text = "De momentele windsnelheid is "+str(windSpeed_var)+ "km/u"
                        json_data = json.dumps(
                            {'top_text': top_text,
                            'scene': scene})
                        yield f"data:{json_data}\n\n"
                        time.sleep(5)
                        ranCount = 0
                        active = False 
                    else:
                        print("* Scene 108 activating")
                        scene = 108
                        top_text = "De momentele windsnelheid is "+str(windSpeed_var)+ "km/u"
                        json_data = json.dumps(
                            {'top_text': top_text,
                            'scene': scene})
                        yield f"data:{json_data}\n\n"
                        time.sleep(5)
                        ranCount = 0
                        active = False        
                        
                        
                                        
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

if __name__ == '__main__':
    #Timer(1, open_browser).start()
    app.run(debug=True, threaded=True)
