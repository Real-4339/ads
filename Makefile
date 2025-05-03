CELERY_VERSION = 1.2.1
CELERY_DOCKER_IMAGE = celery-image
CELERY_DOCKER_NAME = celery-container

VIS_VERSION = 1.0.0
VIS_DOCKER_IMAGE = log-visualizer-image
VIS_DOCKER_NAME = log-visualizer-container

MAIN_VERSION = 2.1.6
MAIN_DOCKER_IMAGE = ads-image
MAIN_DOCKER_NAME = ads-container

CELERY_DOCKER_FILE = ./ads_celery/ci/Dockerfile
MAIN_DOCKER_FILE = ./ads/ci/Dockerfile
VIS_DOCKER_FILE = ./visualization/Dockerfile

DOCKER_COMPOSE_FILE = ./docker-compose.yml
APP_DOTENV_FILE = .env

# COLORED OUTPUT
ccinfo  = $(shell tput setaf 6)
ccwarn  = $(shell tput setaf 3)
ccerror = $(shell tput setaf 1)
ccok  = $(shell tput setaf 2)
ccreset = $(shell tput sgr0)
INFO  = $(ccinfo)[INFO] |$(ccreset)
WARN  = $(ccwarn)[WARN] |$(ccreset)
ERROR  = $(ccerror)[ERROR] |$(ccreset)
OK   = $(ccok)[OK] |$(ccreset)


.PHONY: main clean build up down logs

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  start_docker       Start the Celery and Log Visualizer Docker containers"
	@echo "  start_main         Start the Ads Docker container"
	@echo "  restart_docker     Restart the Celery and Log Visualizer Docker containers without cleaning."
	@echo "  rebuild_visual     Rebuild the Log Visualizer Docker image and start the container"

	@echo "  stop_docker        Stop the Celery and Log Visualizer Docker containers with cleaning."
	@echo "  clean_main         Clean up the Ads Docker container and image"
	@echo "  up                 Start the Docker containers (Celery and Log Visualizer)"
	@echo "  down               Stop the Docker containers (Celery and Log Visualizer)"
	@echo "  logs               Show the logs of the Docker containers (Celery and Log Visualizer)"
	@echo "  help               Show this help message"

	@echo "Used for development and testing purposes only."
	@echo "  build_celery       Build the Celery Docker image"
	@echo "  build_visual       Build the Log Visualizer Docker image"
	
	@echo "  clean_celery       Clean up the Celery Docker container and image"
	@echo "  clean_visual       Clean up the Log Visualizer Docker container and image"
	@echo "  dev_main           Run the Ads module localy, not in Docker, CELERY_BROKER_URL have to be changed from redis name to localhost"


clean_celery:
	@echo "${INFO} Cleaning up..."
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "__pycache__" -exec rm -rf {} \;
	@if docker images | grep -q ${CELERY_DOCKER_IMAGE}; then \
		echo "${INFO} Deleting the docker image ${CELERY_DOCKER_IMAGE}:${CELERY_VERSION}..."; \
		docker image rm ${CELERY_DOCKER_IMAGE}:${CELERY_VERSION}; \
	fi
	@echo "${OK} Cleaned up! (removed .pyc files and __pycache__ folders)"

clean_visual:
	@echo "${INFO} Cleaning up..."
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "__pycache__" -exec rm -rf {} \;
	@if docker images | grep -q ${VIS_DOCKER_IMAGE}; then \
		echo "${INFO} Deleting the docker image ${VIS_DOCKER_IMAGE}:${VIS_VERSION}..."; \
		docker image rm ${VIS_DOCKER_IMAGE}:${VIS_VERSION}; \
	fi

	@echo "${OK} Cleaned up! (removed .pyc files and __pycache__ folders)"

build_celery:
	@echo "${INFO} Building the Docker image ${CELERY_DOCKER_IMAGE}:${CELERY_VERSION}..."
	@docker build --no-cache -t ${CELERY_DOCKER_IMAGE}:${CELERY_VERSION} -f ${CELERY_DOCKER_FILE} .
	@echo "${OK} Docker image ${CELERY_DOCKER_IMAGE}:${CELERY_VERSION} built successfully!"

build_visual:
	@echo "${INFO} Building the Docker image ${VIS_DOCKER_IMAGE}:${VIS_VERSION}..."
	@docker build --no-cache -t ${VIS_DOCKER_IMAGE}:${VIS_VERSION} -f ${VIS_DOCKER_FILE} .
	@echo "${OK} Docker image ${VIS_DOCKER_IMAGE}:${VIS_VERSION} built successfully!"

up:
	@echo "${INFO} Starting the Docker container ${CELERY_DOCKER_NAME}..."
	@echo "${INFO} Starting the Docker container ${VIS_DOCKER_NAME}..."
	@docker-compose -f ${DOCKER_COMPOSE_FILE} up -d
	@echo "${OK} Docker container ${CELERY_DOCKER_NAME} started successfully!"
	@echo "${OK} Docker container ${VIS_DOCKER_NAME} started successfully!"

down:
	@echo "${INFO} Stopping the Docker container ${CELERY_DOCKER_NAME}..."
	@echo "${INFO} Stopping the Docker container ${VIS_DOCKER_NAME}..."
	@docker-compose -f ${DOCKER_COMPOSE_FILE} down -v --remove-orphans
	@echo "${OK} Docker container ${CELERY_DOCKER_NAME} stopped successfully!"
	@echo "${OK} Docker container ${VIS_DOCKER_NAME} stopped successfully!"

logs:
	@echo "${INFO} Showing the logs of the Docker container ${CELERY_DOCKER_NAME}..."
	@echo "${INFO} Showing the logs of the Docker container ${VIS_DOCKER_NAME}..."
	@docker-compose -f ${DOCKER_COMPOSE_FILE} logs -f
	@echo "${OK} Logs of the Docker container ${CELERY_DOCKER_NAME} displayed successfully!"
	@echo "${OK} Logs of the Docker container ${VIS_DOCKER_NAME} displayed successfully!"

dev_main:
	@echo "Running ads module..."
	@python3.11 -m ads

	@echo "Done!"

start_docker: build_celery build_visual up
restart_docker: down up
stop_docker: down clean_celery clean_visual

rebuild_visual: down clean_visual build_visual up

build_main:
	@echo "${INFO} Building the Docker image ${MAIN_DOCKER_IMAGE}:${MAIN_VERSION}..."
	@docker build --no-cache -t ${MAIN_DOCKER_IMAGE}:${MAIN_VERSION} -f ${MAIN_DOCKER_FILE} .
	@echo "${OK} Docker image ${MAIN_DOCKER_IMAGE}:${MAIN_VERSION} built successfully!"

start_main:
	@echo "${INFO} Starting the Docker container ${MAIN_DOCKER_NAME}..."
	@docker run --name ${MAIN_DOCKER_NAME} -it --rm\
		--network code_ads-network \
		--env-file ${APP_DOTENV_FILE} \
		-v $(shell pwd):/app \
		${MAIN_DOCKER_IMAGE}:${MAIN_VERSION}
	@echo "${OK} Docker container ${MAIN_DOCKER_NAME} started successfully!"

clean_main:
	@echo "${INFO} Removing the Docker container ${MAIN_DOCKER_NAME}..."
	@docker rm -f ${MAIN_DOCKER_NAME} || true
	@echo "${OK} Docker container ${MAIN_DOCKER_NAME} removed successfully!"
	@echo "${INFO} Cleaning up..."
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "__pycache__" -exec rm -rf {} \;
	@if docker images | grep -q ${MAIN_DOCKER_IMAGE}; then \
		echo "${INFO} Deleting the docker image ${MAIN_DOCKER_IMAGE}:${MAIN_VERSION}..."; \
		docker image rm ${MAIN_DOCKER_IMAGE}:${MAIN_VERSION}; \
	fi
	@echo "${OK} Cleaned up! (removed .pyc files and __pycache__ folders)"