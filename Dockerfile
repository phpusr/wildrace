FROM python:3.8
MAINTAINER phpusr

ENV PYTHONBUFFERED 1
ENV PORT 8000

WORKDIR /app/

# Install dependencies
COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pipenv \
    && pipenv lock --requirements > requirements.txt \
    && pip install -r requirements.txt \
    && pipenv --rm \
    && pip uninstall -y pipenv \
    && rm Pipfile Pipfile.lock requirements.txt

# Add user
RUN useradd user
USER user

# Copy source files
COPY scripts/docker_run.sh /usr/local/bin/wildrace
COPY manage.py .
COPY backend .

CMD ./manage.py migrate && wildrace $PORT