import os
import requests
import json
import numpy as np
import pandas as pd
import datetime
from flask import Flask, render_template, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)

API_KEY = '03b8c4d4af0e87a4c9ac54e1c7b30517'

city_list = ['Chicago', 'West Des Moines', 'Seattle']


def get_current():
    # get current weather for the cities in city_list
    # then save the data to BigQuery table
    # run every 3 hours

    for city in city_list:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
        r_c = requests.get(url).json()
        current = {
            'city': r_c['name'],
            'city_id': r_c['id'],
            'time': datetime.datetime.fromtimestamp(r_c['dt']),
            'longitude': r_c['coord']['lon'],
            'latitude': r_c['coord']['lat'],
            'weather_id': r_c['weather'][0]['id'],
            'weather': r_c['weather'][0]['main'],
            'weather_dec': r_c['weather'][0]['description'],
            'weather_icon': r_c['weather'][0]['icon'],
            'temp': round(r_c['main']['temp'], 1),
            'feels_like': round(r_c['main']['feels_like'], 1),
            'temp_min': round(r_c['main']['temp_min'], 1),
            'temp_max': round(r_c['main']['temp_max'], 1),
            'pressure': r_c['main']['pressure'],
            'humidity': r_c['main']['humidity'],
            'visibility': r_c['visibility'],
            'wind_speed': r_c['wind']['speed'],
            'wind_direction': r_c['wind']['deg'],
            'cloudiness': r_c['clouds']['all'],
            'timezone': r_c['timezone'],
            'sunrise': r_c['sys']['sunrise'],
            'sunset': r_c['sys']['sunset'],
            'country': r_c['sys']['country']
        }
        row = pd.DataFrame(current, index=[0])

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

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    r_c = requests.get(url).json()

    current = {
        'city': r_c['name'],
        'city_id': r_c['id'],
        'time': datetime.datetime.fromtimestamp(r_c['dt']),
        'longitude': r_c['coord']['lon'],
        'latitude': r_c['coord']['lat'],
        'weather_id': r_c['weather'][0]['id'],
        'weather': r_c['weather'][0]['main'],
        'weather_dec': r_c['weather'][0]['description'],
        'weather_icon': r_c['weather'][0]['icon'],
        'temp': round(r_c['main']['temp'], 1),
        'feels_like': round(r_c['main']['feels_like'], 1),
        'temp_min': round(r_c['main']['temp_min'], 1),
        'temp_max': round(r_c['main']['temp_max'], 1),
        'pressure': r_c['main']['pressure'],
        'humidity': r_c['main']['humidity'],
        'visibility': r_c['visibility'],
        'wind_speed': r_c['wind']['speed'],
        'wind_direction': r_c['wind']['deg'],
        'cloudiness': r_c['clouds']['all'],
        'timezone': r_c['timezone'],
        'sunrise': r_c['sys']['sunrise'],
        'sunset': r_c['sys']['sunset'],
        'country': r_c['sys']['country']
    }


    return render_template("main.html", weather_dict = current)




if __name__ == "__main__":
    app.run(host = '127.0.0.1', debug = True, port=int(os.environ.get("PORT", 8080)))
