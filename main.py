import os
import requests
import json
import numpy as np
import pandas as pd
import datetime
from flask import Flask, render_template, request, jsonify
from dateutil.relativedelta import relativedelta
from google.cloud import bigquery

app = Flask(__name__)

API_KEY = '03b8c4d4af0e87a4c9ac54e1c7b30517'
project_id = 'weather-tracker-344603'
dataset_id = 'weather_data'

# city_list = ['Chicago', 'West Des Moines', 'Seattle']


@app.route("/", methods = ['GET', 'POST'])
def home_page():

    # get current available city in the data
    client = bigquery.Client(project=project_id)
    query = f'''
    SELECT * FROM {project_id}.{dataset_id}.city
    '''
    query_job = client.query(query)
    cities = query_job.to_dataframe()
    city_list = [c for c in cities['city'].to_list() if c != 'None']

    # get input from user
    city = str(request.form.get('city'))
    if city not in city_list:
        city_list.append(city)
        table_id = f"{project_id}.{dataset_id}.city"
        city_df = pd.DataFrame({
            'city': city
        }, index = [0])
        client = bigquery.Client(project = project_id)
        job = client.load_table_from_dataframe(
            city_df, table_id
        )
        job.result()

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    r_c = requests.get(url).json()

    # current weather from the API
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
        'sunrise': datetime.datetime.fromtimestamp(r_c['sys']['sunrise']),
        'sunset': datetime.datetime.fromtimestamp(r_c['sys']['sunset']),
        'country': r_c['sys']['country']
    }

    # recent temperature trend of the city
    query = f'''
    SELECT time, temp AS actual_temp
    FROM {project_id}.{dataset_id}.actual
    WHERE city = '{city}'
    ORDER BY time
    '''
    query_job = client.query(query)
    actual = query_job.to_dataframe()
    actual['time'] = actual.time.dt.tz_convert(tz='US/Central').dt.tz_localize(None)
    # [c for c in data['city'].to_list() if c != 'None']

    query = f'''
    SELECT created_at, forecast_time AS time, temp AS forecast_temp
    FROM {project_id}.{dataset_id}.forecast
    WHERE city = '{city}'
    ORDER BY created_at, forecast_time
    '''
    query_job = client.query(query)
    forecast = query_job.to_dataframe()
    forecast = forecast[forecast['time'] >= datetime.datetime.now()]
    forecast = forecast.drop_duplicates(subset=['time'], keep='last')
    forecast.drop('created_at', axis=1, inplace=True)

    data = actual.merge(forecast, on='time', how='outer')

    labels = data['time'].dt.strftime("%Y-%m-%d %H:00")
    value1 = data['actual_temp'].values.tolist()
    value2 = data['forecast_temp'].values.tolist()

    return render_template("main.html",
                           weather_dict = current,
                           table1 = [data.to_html(classes = 'data')],
                           title1 = data.columns.values,
                           city_name = city,
                           labels = labels,
                           value1 = value1,
                           value2 = value2
                           )


if __name__ == "__main__":
    app.run(host = '127.0.0.1', debug = True, port=int(os.environ.get("PORT", 8080)))
