import os
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home_page():


    return render_template("main.html")




if __name__ == "__main__":
    app.run(host = '127.0.0.1', debug = True, port=int(os.environ.get("PORT", 8080)))