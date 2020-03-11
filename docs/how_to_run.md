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

`make run` - Run frontend and backend in developed mode

`make daphne` - Run project with daphne server

### Build

`make install` - Install frontend and backend dependencies

`make build` - Build frontend and backend, test project and build a docker container

`make build-no-test` - Build without test

`make build-frontend` - Build a frontend project

`make build-backend` - Build a backend project

### Test

`make test` - Test project

`make coverage` - Test project and run [Coverage.py]((https://coverage.readthedocs.io/))

`make flake8` - Test [Flake8](https://flake8.pycqa.org/en/latest/)

### Docker

`make docker-build` - Build a docker container

### Heroku

`make heroku-logs` - Show heroku logs

`make heroku-push-local` - Push local docker image to your Heroku app and release it

`make heroku-build-push` - Does `heroku-push`, then `heroku-release`

`make heroku-push` - Build, then push Docker image to deploy your Heroku app

`make heroku-release` - Release previously pushed Docker image to your Heroku app

`make heroku-rm` - Remove the process type from your app

`make heroku-run` - Build, then run the docker image locally
