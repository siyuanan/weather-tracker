# define runtime
FROM python:3.8

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# environment parameters
ENV APP_HOME /app
WORKDIR $APP_HOME

# copy source code
COPY . ./

# install dependencies
RUN python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt

# run app
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
