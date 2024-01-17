# pull official base image
FROM python:3.8-slim-buster

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apt-get update
RUN apt-get install -y libpq-dev gcc


# RUN apt install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 \
#   libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 \
#   fonts-liberation libappindicator3-1 libnss3 lsb-release xdg-utils

COPY . /app

# install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

