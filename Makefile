APP_NAME=wildrace
APP_SERVICE=web
SPACE=18

# src: https://gist.github.com/prwhite/8168133#gistcomment-2833138
help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-${SPACE}s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Run

run: ## Run frontend and backend in developed mode
	@echo "=== Run frontend ==="
	cd frontend && yarn serve &
	@echo "=== Run backend ==="
	pipenv run ./manage.py migrate && pipenv run ./manage.py runserver

daphne:	## Run project with daphne server
	@echo "=== Run daphne ==="
	cd backend && pipenv run daphne app.asgi:application -b 0.0.0.0 -p 8000

##@ Build

install: ## Install frontend and backend dependencies
	@echo "=== Build dependencies ==="
	cd frontend && yarn install
	pipenv install --dev

build: build-frontend build-backend test docker-build ## Build frontend and backend, test project and build a docker container
	@echo "=== Build finished ==="

build-no-test: build-frontend build-backend docker-build ## Build without test
	@echo "=== Build finished ==="

build-frontend: ## Build a frontend project
	@echo "=== Build frontend ==="
	cd frontend && yarn build

build-backend: ## Build a backend project
	@echo "=== Build backend ==="
	pipenv run ./manage.py collectstatic --clear --no-input

##@ Test

test: flake8 ## Test project
	@echo "=== Test backend ==="
	pipenv run ./manage.py test

coverage: ## Test project and run Coverage.py
	cd backend && pipenv run coverage run; \
	pipenv run coverage report && pipenv run coverage html \
	&& chromium ../.coverage_html/index.html

flake8: ## Test with Flake8
	@echo "=== flake8 ==="
	cd backend && pipenv run flake8

##@ Docker

docker-build: ## Build a docker container
	docker-compose build

##@ Heroku

heroku-logs: ## Show heroku logs
	heroku logs -t -a $(APP_NAME)

heroku-push-local: ## Push a local docker image to your Heroku app and release it
	docker tag phpusr/wildrace registry.heroku.com/wildrace/web
	docker push registry.heroku.com/wildrace/web
	$(MAKE) heroku-release

heroku-build-push: heroku-push heroku-release ## Does 'heroku-push', then 'heroku-release'

# required "heroku container:login"
heroku-push: ## Build, then push Docker image to deploy your Heroku app
	heroku container:push $(APP_SERVICE) -a $(APP_NAME)

heroku-release: ## Release previously pushed Docker image to your Heroku app
	heroku container:release $(APP_SERVICE) -a $(APP_NAME)

heroku-rm: ## Remove the process type from your app
	heroku container:rm $(APP_SERVICE) -a $(APP_NAME)

heroku-run: ## Build, then run the docker image locally
	heroku container:run $(APP_SERVICE) -a $(APP_NAME)
