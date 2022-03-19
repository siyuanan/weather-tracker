import os
import requests
import json
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)

API_KEY = os.environ['API_KEY']

city_list = ['Chicago', 'West Des Moines', 'Seattle']

def get_current():
    # get current weather for the cities in city_list
    # then save the data to BigQuery table
    # run every 3 hours

    return

def get_forecast():
    # get most recent forecast
    # save the data to BigQuery table
    # run every 3 hours
    return

@app.route("/", methods=['GET', 'POST'])
def home_page():
    # get input from user
    city = request.form.get('city')
    if city not in city_list:
        city_list.append(city)

    for city in city_list:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
        r = requests.get(url).json()
        weather_dict = {
            'city': r['name'],
            'weather': r['weather'][0]['main'],
            'temperature': f"{round(float(r['main']['temp']), 1)} °C",
            'humidity': f"{r['main']['humidity']}%"
        }

    return render_template("main.html", weather_dict = weather_dict)




if __name__ == "__main__":
    app.run(host = '127.0.0.1', debug = True, port=int(os.environ.get("PORT", 8080)))
