FROM python:3.8
MAINTAINER phpusr

ENV PYTHONBUFFERED 1

# Copy run script
COPY ./scripts/docker_run.sh /bin/wildrace.sh
RUN chmod +rx /bin/wildrace.sh

# Install dependencies
COPY ./backend/Pipfile /app/Pipfile
COPY ./backend/Pipfile.lock /app/Pipfile.lock
RUN cd /app \
    && pip install --upgrade pipenv \
    && pipenv lock --requirements > requirements.txt \
    && pip install -r requirements.txt

# Copy source files
COPY backend /app
WORKDIR /app

# Add user
RUN mkdir -p /vol/web/static
RUN useradd user
RUN chown -R user:user /vol
RUN chmod -R 700 /vol/web
USER user

CMD /bin/wildrace.sh $PORT