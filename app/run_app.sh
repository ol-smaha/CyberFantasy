#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate
python manage.py collectstatic --noinput  # need to gunicorn download static
gunicorn --access-logfile - --workers 4 --timeout 120 --reload \
  --bind app:8000 core.wsgi:application
