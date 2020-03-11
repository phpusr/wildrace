APP_NAME=wildrace
APP_SERVICE=web

GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)
HELP_FUN = \
    %help; \
    while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
    print "usage: make [target]\n\n"; \
    for (sort keys %help) { \
    	print "${WHITE}$$_:${RESET}\n"; \
    	for (@{$$help{$$_}}) { \
    		$$sep = " " x (20 - length $$_->[0]); \
    		print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
    	}; \
    	print "\n"; \
	}

help: ##@help Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

### Run ###

run: ##@run Run frontend and backend in developed mode
	@echo "=== Run frontend ==="
	cd frontend && yarn serve &
	@echo "=== Run backend ==="
	pipenv run ./manage.py migrate && pipenv run ./manage.py runserver

daphne:	##@run Run project with daphne server
	@echo "=== Run daphne ==="
	cd backend && pipenv run daphne app.asgi:application -b 0.0.0.0 -p 8000

### Build ###

install: ##@build Install frontend and backend dependencies
	@echo "=== Build dependencies ==="
	cd frontend && yarn install
	pipenv install --dev

build: build-frontend build-backend test docker-build ##@build Build frontend and backend, test project and build a docker container
	@echo "=== Build finished ==="

build-no-test: build-frontend build-backend docker-build ##@build Build without test
	@echo "=== Build finished ==="

build-frontend: ##@build Build a frontend project
	@echo "=== Build frontent ==="
	cd frontend && yarn build

build-backend: ##@build Build a backend project
	@echo "=== Build backend ==="
	pipenv run ./manage.py collectstatic --clear --no-input

### Test ###

test: flake8 ##@test Test project
	@echo "=== Test backend ==="
	pipenv run ./manage.py test

coverage: ##@test Test project and run Coverage.py
	cd backend && pipenv run coverage run; \
	pipenv run coverage report && pipenv run coverage html \
	&& chromium ../.coverage_html/index.html

flake8: ##@test Test with Flake8
	@echo "=== flake8 ==="
	cd backend && pipenv run flake8

### Docker ###

docker-build: ##@docker Build a docker container
	docker-compose build

### Heroku ###

heroku-logs: ##@heroku Show heroku logs
	heroku logs -t -a $(APP_NAME)

heroku-push-local: ##@heroku Push a local docker image to your Heroku app and release it
	docker tag phpusr/wildrace registry.heroku.com/wildrace/web
	docker push registry.heroku.com/wildrace/web
	$(MAKE) heroku-release

heroku-build-push: heroku-push heroku-release ##@heroku Does 'heroku-push', then 'heroku-release'

heroku-push: ##@heroku Build, then push Docker image to deploy your Heroku app
	heroku container:push $(APP_SERVICE) -a $(APP_NAME)

heroku-release: ##@heroku Release previously pushed Docker image to your Heroku app
	heroku container:release $(APP_SERVICE) -a $(APP_NAME)

heroku-rm: ##@heroku Remove the process type from your app
	heroku container:rm $(APP_SERVICE) -a $(APP_NAME)

heroku-run: ##@heroku Build, then run the docker image locally
	heroku container:run $(APP_SERVICE) -a $(APP_NAME)
