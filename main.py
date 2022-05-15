import os
import requests
import json
import numpy as np
import pandas as pd
import datetime
import re
from flask import Flask, render_template, request, jsonify
from dateutil.relativedelta import relativedelta
from google.cloud import bigquery
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)

API_KEY = '03b8c4d4af0e87a4c9ac54e1c7b30517'
project_id = 'weather-tracker-344603'
dataset_id = 'weather_data'


@app.route("/", methods = ['GET', 'POST'])
@app.route("/home", methods = ['GET', 'POST'])
def home():
    # get input from user
    city = str(request.form.get('city'))

    # get current available city in the data
    client = bigquery.Client(project=project_id)
    query = f'''
    SELECT * FROM {project_id}.{dataset_id}.city
    '''
    query_job = client.query(query)
    cities = query_job.to_dataframe()
    city_list = [c for c in cities['city'].to_list() if c != 'None']

    if city not in city_list:
        city_list.append(city)
        table_id = f"{project_id}.{dataset_id}.city"
        city_df = pd.DataFrame({
            'city': city
        }, index=[0])
        client = bigquery.Client(project=project_id)
        job = client.load_table_from_dataframe(
            city_df, table_id
        )
        job.result()

        return render_template("home.html")


@app.route("/forecast", methods = ['GET', 'POST'])
def weather_forecast():
    # default city
    # city = 'Chicago'

    # get input from user
    city = str(request.form.get('city'))

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
    client = bigquery.Client(project=project_id)
    query = f'''
    SELECT time AS time_utc, temp AS actual_temp
    FROM {project_id}.{dataset_id}.actual
    WHERE city = '{city}'
    ORDER BY time
    '''
    query_job = client.query(query)
    actual = query_job.to_dataframe()
    actual['time_list'] = actual['time_utc'].astype(str).apply(lambda x: re.split(' |:|-', x))
    actual['time'] = actual['time_list'].apply(
        lambda x: datetime.datetime(int(x[0]), int(x[1]), int(x[2]), int(x[3])) + relativedelta(hours=-5))
    actual_time = actual['time'].max()

    query = f'''
    SELECT created_at, forecast_time AS time, temp AS forecast_temp, weather_icon
    FROM {project_id}.{dataset_id}.forecast
    WHERE city = '{city}'
    ORDER BY created_at, forecast_time
    '''
    query_job = client.query(query)
    forecast_all = query_job.to_dataframe()
    forecast_all = forecast_all[forecast_all['time'] > actual_time]
    forecast = forecast_all.drop_duplicates(subset=['time'], keep='last')
    forecast.drop('created_at', axis=1, inplace=True)
    forecast.reset_index(drop=True, inplace=True)

    # ARIMA forecast
    model = ARIMA(actual['actual_temp'], order = (2, 1, 1)).fit()
    temp_model = round(model.forecast().values[0], 1)
    temp_api = forecast.loc[0, 'forecast_temp']
    fcst_time = forecast.loc[0, 'time']
    actual['ARIMA in-sample'] = model.predict()
    actual_sub = actual.tail(80)

    # forecast made on different time (created_at)
    fcst2 = forecast_all[forecast_all['time'] == fcst_time][['created_at', 'time', 'forecast_temp']]
    fcst2.sort_values('created_at', inplace = True)

    # weather forecast icon
    icon_dict = {}
    for i in range(8):
        icon_dict[str(forecast.loc[i, 'time']).split(' ')[1]] = forecast.loc[i, 'weather_icon']
    # forecast.drop('weather_icon', axis=1, inplace=True)

    # combine all data
    data = actual_sub[[
        'time', 'actual_temp', 'ARIMA in-sample'
    ]].merge(
        forecast[['time', 'forecast_temp']],
        on='time',
        how='outer'
    ).fillna(0)

    labels = list(data['time'].astype(str))
    value1 = data['actual_temp'].values.tolist()
    value2 = data['ARIMA in-sample'].values.tolist()
    value3 = data['forecast_temp'].values.tolist()

    return render_template("forecast.html",
                           weather_dict = current,
                           table1 = [data.to_html(classes = 'data')],
                           title1 = data.columns.values,
                           city_name = city,
                           labels = labels,
                           value1 = value1,
                           value2 = value2,
                           value3 = value3,
                           temp_model = temp_model,
                           temp_api = temp_api,
                           fcst_time = fcst_time,
                           icon_dict = icon_dict,
                           fcst2 = [fcst2.to_html(classes = 'data')],
                           title2 = fcst2.columns.values
                           )


if __name__ == "__main__":
    app.run(host = '127.0.0.1', debug = True, port=int(os.environ.get("PORT", 8080)))
