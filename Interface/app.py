#import library
from flask import Flask, Response, render_template
import json

from datetime import datetime

#define open browser
import webbrowser
from threading import Timer

#import for API (weather)
import requests

import time

api_address='http://api.openweathermap.org/data/2.5/weather?APPID=a62699263199cff6bc9755b6529c08db&q='
city = "Rotterdam"
url = api_address + city

#define app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-data')
def get_data():
    def generate_random_data():
        while True:
            json_temp = requests.get(url).json()
            tempa = json_temp['main']['temp'] - 273.15

            print(tempa)

            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Current Time =", current_time)

            json_data = json.dumps(
                {'temperature': tempa,
                 'time': current_time})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(generate_random_data(), mimetype='text/event-stream')

# def open_browser():
#       webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    #Timer(1, open_browser).start()
    app.run(debug=True, threaded=True)

def temperature():
    return json_temp['main']['temp'] - 273.15
