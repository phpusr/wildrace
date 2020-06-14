#!/bin/sh

./manage.py wait_for_db && celery worker -A tasks -B --scheduler django &
./manage.py wait_for_db && daphne app.asgi:application -b 0.0.0.0 -p $1
