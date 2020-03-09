#!/bin/bash

export DJANGO_SETTINGS_MODULE=app.settings.prod

daphne app.asgi:application