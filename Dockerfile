FROM node:22-alpine3.19 AS frontend-build

ENV NODE_OPTIONS=--openssl-legacy-provider

WORKDIR /opt/app

RUN apk update && apk add git

COPY frontend/package.json .
COPY frontend/yarn.lock .

RUN yarn install

COPY frontend .

RUN npm run build

FROM python:3.13-alpine3.22

ENV PYTHONBUFFERED 1
ENV DJANGO_DEBUG False

# Add user
RUN adduser -S -D user

WORKDIR /opt/app/

# Install dependencies
COPY Pipfile.lock ./
RUN pip install --upgrade pipenv \
    && pipenv requirements > requirements.txt \
    && pip install -r requirements.txt \
    && pip uninstall -y pipenv \
    && rm Pipfile.lock requirements.txt

# Copy source files
COPY manage.py .
COPY backend .
COPY --from=frontend-build /opt/app/dist app/static/front

# Collect static files and delete source files
RUN ./manage.py collectstatic --no-input -c

USER user

CMD ./manage.py migrate && ./manage.py wait_for_db \
    && daphne app.asgi:application -b 0.0.0.0 -p 8000; \
    celery --app tasks worker --beat --scheduler django --loglevel=info
