
APP_NAME=wildrace
APP_SERVICE=web

main:
	@echo "This is Makefile for wildrace app"

build: build_frontend build_backend
	@echo "=== Build finished ==="

build_frontend:
	@echo "=== Build frontent ==="
	cd frontend && yarn build

build_backend:
	@echo "=== Build backend ==="

heroku_logs:
	heroku logs -t -a $(APP_NAME)

# builds, then pushes Docker images to deploy your Heroku app
heroku_push:
	heroku container:push $(APP_SERVICE) -a $(APP_NAME)

# Releases previously pushed Docker images to your Heroku app
heroku_release:
	heroku container:release $(APP_SERVICE) -a $(APP_NAME)

# remove the process type from your app
heroku_rm:
	heroku container:rm $(APP_SERVICE) -a $(APP_NAME)

# builds, then runs the docker image locally
heroku_run:
	heroku container:run $(APP_SERVICE) -a $(APP_NAME)
