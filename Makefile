
APP_NAME=wildrace
APP_SERVICE=web

export DJANGO_SETTINGS_MODULE=app.settings.prod

main:
	@echo "This is Makefile for wildrace app"

shell:
	cd backend && pipenv shell

run-prod:
	@echo "=== Run Production version"
	cd backend && pipenv run daphne app.asgi:application -b 0.0.0.0 -p 8000

### Build ###

build: build-frontend build-backend
	@echo "=== Build finished ==="

build-frontend:
	@echo "=== Build frontent ==="
	cd frontend && yarn build

build-backend:
	@echo "=== Build backend ==="
	cd backend && pipenv run ./manage.py collectstatic --clear --no-input

### Heroku ###

heroku-logs:
	heroku logs -t -a $(APP_NAME)

heroku: heroku-push heroku-release

# builds, then pushes Docker images to deploy your Heroku app
heroku-push:
	heroku container:push $(APP_SERVICE) -a $(APP_NAME)

# Releases previously pushed Docker images to your Heroku app
heroku-release:
	heroku container:release $(APP_SERVICE) -a $(APP_NAME)

# remove the process type from your app
heroku-rm:
	heroku container:rm $(APP_SERVICE) -a $(APP_NAME)

# builds, then runs the docker image locally
heroku-run:
	heroku container:run $(APP_SERVICE) -a $(APP_NAME)
