How to run
==========

## You need to install

- [Python 3](https://www.python.org/)
    - [Pipenv](https://pipenv.readthedocs.io/en/latest/)
- [Node.js](https://nodejs.org/en/)
    - [yarn](https://yarnpkg.com/)
- [Make](http://www.man7.org/linux/man-pages/man1/make.1.html)
- [Docker](https://www.docker.com/) (optional)
    - [Docker Compose](https://docs.docker.com/compose/) (optional)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) (optional)

## Run project in developed mode

Install dependencies

```
make install
```

And run in developed mode

```
make run
```

## Run project in production mode (needs Docker)

Install dependencies and build a docker container

```
make install build-no-test
```

Start docker containers

```
docker-compose up
```

## Makefile commands

### Run

`make run` - run frontend and backend in developed mode

`make daphne` - run project with daphne server

### Build

`make install` - install frontend and backend dependencies

`make build` - build frontend and backend, test project and build a docker container

`make build-frontend` - build a frontend project

`make build-backend` - build a backend project

### Test

`make test` - test project

`make coverage` - test project and run [Coverage.py]((https://coverage.readthedocs.io/))

`make flake8` - test [Flake8](https://flake8.pycqa.org/en/latest/)

### Docker

`make docker-build` - build a docker container

### Heroku

`make heroku-logs` - show heroku logs

`make heroku-push-local` - push local docker image to your Heroku app and release it

`make heroku-build-push` - `heroku-push` and `heroku-release`

`make heroku-push` - builds, then pushes Docker images to deploy your Heroku app

`make heroku-release` - releases previously pushed Docker images to your Heroku app

`make heroku-rm` - remove the process type from your app

`make heroku-run` - builds, then runs the docker image locally
