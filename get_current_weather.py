import os
import requests
import json
import numpy as np
import pandas as pd
import datetime
from google.cloud import bigquery

project_id  = 'weather-tracker-344603'
dataset_id  = 'weather_data'
current_table = 'actual'
forecast_table = 'forecast'

city_list = ['Chicago', 'West Des Moines', 'Seattle']
# city_list = ['Los Angeles', 'Las Vegas']

def get_current_weather():
    # get current weather for the cities in city_list
    # then save the data to BigQuery table
    # run every 3 hours

    table_id = f"{project_id}.{dataset_id}.{current_table}"

    for city in city_list:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=03b8c4d4af0e87a4c9ac54e1c7b30517"
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

        # print(row)

        # Construct a BigQuery client object.
        client = bigquery.Client()
        # Make an API request.
        job = client.load_table_from_dataframe(
            row, table_id
        )
        job.result()  # Wait for the job to complete.

    return True
