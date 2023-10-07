FROM python:3.8

ENV PYTHONBUFFERED 1
ENV DJANGO_DEBUG False

WORKDIR /app/

# Install dependencies
COPY Pipfile.lock ./
RUN pip install --upgrade pipenv \
    && pipenv requirements > requirements.txt \
    && pip install -r requirements.txt \
    && pip uninstall -y pipenv \
    && rm Pipfile.lock requirements.txt

# Add user
RUN useradd user
USER user

# Copy source files
COPY scripts/docker_run.sh /usr/local/bin/wildrace
COPY manage.py .
COPY backend .

CMD ./manage.py migrate && wildrace 8000
