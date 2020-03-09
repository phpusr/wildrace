FROM python:3.8
MAINTAINER phpusr

ENV PYTHONBUFFERED 1

# Install dependencies
COPY Pipfile Pipfile.lock /app/
RUN cd /app \
    && pip install --upgrade pipenv \
    && pipenv lock --requirements > requirements.txt \
    && pip install -r requirements.txt \
    && pipenv --rm \
    && pip uninstall -y pipenv

# Copy source files
COPY . /app
WORKDIR /app
RUN rm Pipfile Pipfile.lock \
    && chmod +rx scripts/docker_run.sh \
    && ln -s /app/scripts/docker_run.sh /bin/wildrace

# Add user
RUN mkdir -p /vol/web/static
RUN useradd user
RUN chown -R user:user /vol
RUN chmod -R 700 /vol/web
USER user

CMD ./manage.py migrate && /bin/wildrace $PORT