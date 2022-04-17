# function on Google Cloud Functions
# to gather actual and forecast weather data and load into BigQuery table
import os
import requests
import json
import numpy as np
import pandas as pd
import datetime
from google.cloud import bigquery

project_id = 'weather-tracker-344603'
dataset_id = 'weather_data'
current_table = 'actual'
forecast_table = 'forecast'

# city_list = ['Chicago', 'West Des Moines', 'Seattle']
# city_list = ['Los Angeles', 'Las Vegas']

# the two inputs are not used in the function
# but without the two inputs, the function cannot run on cloud function
def current_weather(event, data):
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
        client = bigquery.Client(project = project_id)
        # Make an API request.
        job = client.load_table_from_dataframe(
            row, table_id
        )
        job.result()  # Wait for the job to complete.

    return True


# function to pull forecast data
def weather_forecast(event, data):
    # get current weather for the cities in city_list
    # then save the data to BigQuery table
    # run every 3 hours

    # get current available city in the data
    client = bigquery.Client(project=project_id)
    query = f'''
    SELECT * FROM {project_id}.{dataset_id}.city
    '''
    query_job = client.query(query)
    cities = query_job.to_dataframe()
    city_list = [c for c in cities['city'].to_list() if c != 'None']

    table_id = f"{project_id}.{dataset_id}.{forecast_table}"

    for city in city_list:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid=03b8c4d4af0e87a4c9ac54e1c7b30517"
        r_f = requests.get(url).json()
        forecast = []
        for i in range(r_f['cnt']):
            forecast.append({
              'city': r_f['city']['name'],
              'city_id': r_f['city']['id'],
              'created_at': datetime.datetime.now(),
              'forecast_time': datetime.datetime.fromtimestamp(r_f['list'][i]['dt']),
              'longitude': r_f['city']['coord']['lon'],
              'latitude': r_f['city']['coord']['lat'],
              'weather_id': r_f['list'][i]['weather'][0]['id'],
              'weather': r_f['list'][i]['weather'][0]['main'],
              'weather_dec': r_f['list'][i]['weather'][0]['description'],
              'weather_icon': r_f['list'][i]['weather'][0]['icon'],
              'temp': round(r_f['list'][i]['main']['temp'], 1),
              'feels_like': round(r_f['list'][i]['main']['feels_like'], 1),
              'temp_min': round(r_f['list'][i]['main']['temp_min'], 1),
              'temp_max': round(r_f['list'][i]['main']['temp_max'], 1),
              'pressure': r_f['list'][i]['main']['pressure'],
              'humidity': r_f['list'][i]['main']['humidity'],
              'visibility': r_f['list'][i]['visibility'],
              'wind_speed': r_f['list'][i]['wind']['speed'],
              'wind_direction': r_f['list'][i]['wind']['deg'],
              'cloudiness': r_f['list'][i]['clouds']['all'],
              'prob': r_f['list'][i]['pop'],
              'timezone': r_f['city']['timezone'],
              'sunrise': r_f['city']['sunrise'],
              'sunset': r_f['city']['sunset'],
              'country': r_f['city']['country'],
              'population': r_f['city']['population']
            })
        rows = pd.DataFrame(forecast)

        # print(row)

        # Construct a BigQuery client object.
        client = bigquery.Client(project = project_id)
        # Make an API request.
        job = client.load_table_from_dataframe(
            rows, table_id
        )
        job.result()  # Wait for the job to complete.

    return True

