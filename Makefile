
APP_NAME=wildrace
APP_SERVICE=web

main:
	@echo "This is Makefile for wildrace app"

daphne:
	@echo "=== Run daphne ==="
	cd backend && pipenv run daphne app.asgi:application -b 0.0.0.0 -p 8000

### Build ###

build: build-frontend build-backend test docker-build
	@echo "=== Build finished ==="

build-frontend:
	@echo "=== Build frontent ==="
	cd frontend && yarn build

build-backend: flake8
	@echo "=== Build backend ==="
	pipenv run ./manage.py collectstatic --clear --no-input

### Test ###

test:
	@echo "=== Test backend ==="
	pipenv run ./manage.py test

coverage:
	cd backend && pipenv run coverage run; \
	pipenv run coverage report && pipenv run coverage html \
	&& chromium ../.coverage_html/index.html

flake8:
	@echo "=== flake8 ==="
	cd backend && pipenv run flake8

### Docker ###

docker-build:
	docker-compose build

### Heroku ###

heroku-logs:
	heroku logs -t -a $(APP_NAME)

heroku-build-push: heroku-push heroku-release

heroku-push-local:
	docker tag phpusr/wildrace registry.heroku.com/wildrace/web
	docker push registry.heroku.com/wildrace/web
	$(MAKE) heroku-release

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
