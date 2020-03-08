FROM python:3.8
MAINTAINER phpusr

ENV PYTHONBUFFERED 1

COPY ./backend/Pipfile /app/Pipfile
COPY ./backend/Pipfile.lock /app/Pipfile.lock

RUN cd /app \
    && pip install --upgrade pipenv \
    && pipenv lock --requirements > requirements.txt \
    && pip install -r requirements.txt

COPY backend /app
WORKDIR /app

RUN mkdir -p /vol/web/static
RUN useradd user
RUN chown -R user:user /vol
RUN chmod -R 700 /vol/web
USER user

CMD daphne app.asgi:application -b 0.0.0.0 -p $PORT
