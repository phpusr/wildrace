#!/bin/sh

celery worker -A tasks -B --scheduler django &
daphne app.asgi:application -b 0.0.0.0 -p $1
