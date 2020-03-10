FROM python:3.8
MAINTAINER phpusr

ENV PYTHONBUFFERED 1
ENV PORT 8000

# Copy run script
COPY ./scripts/docker_run.sh /usr/local/bin/wildrace
RUN chmod +x /usr/local/bin/wildrace

# Install dependencies
COPY Pipfile Pipfile.lock /app/
RUN cd /app \
    && pip install --upgrade pipenv \
    && pipenv lock --requirements > requirements.txt \
    && pip install -r requirements.txt \
    && pipenv --rm \
    && pip uninstall -y pipenv \
    && rm Pipfile Pipfile.lock requirements.txt

# Add user
RUN useradd user
USER user

# Copy source files
COPY backend /app
WORKDIR /app

CMD ./manage.py migrate && wildrace $PORT