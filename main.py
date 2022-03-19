import os
import requests
import json
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_KEY = "03b8c4d4af0e87a4c9ac54e1c7b30517"

city_list = ['Chicago', 'West Des Moines', 'Seattle']


@app.route("/", methods=['GET', 'POST'])
def home_page():
    # get input from user
    city = request.form.get('city')
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
