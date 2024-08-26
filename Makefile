# Default target
.PHONY: all
all: up

# Build all services
.PHONY: build
build:
	docker compose build

# Start all services
.PHONY: up
up:
	mkdir -p database_volume
	docker compose up -d --build

# Stop all services
.PHONY: down
down:
	docker compose down --remove-orphans --volumes

# Stop all services and remove all containers
.PHONY: down-all
down-all:
	@if [ -n "$(shell docker ps -aq)" ]; then \
		for container in $(shell docker ps -aq); do \
			docker rm -f $$container; \
		done \
	fi

# Restart all services
.PHONY: re
re: down-all clean up

# Show logs for all services, or if soecified, for a specific service only, e.g. make logs user-service
.PHONY: logs
logs:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		docker compose logs -f; \
	else \
		docker compose logs -f $(filter-out $@,$(MAKECMDGOALS)); \
	fi


# Pull latest images for all services
.PHONY: pull
pull:
	docker compose pull

# Remove stopped containers and unused images, networks, and volumes
.PHONY: clean
clean:
	@if [ -d "/database_volume" ]; then \
		rm -rf /database_volume; \
	fi

	docker system prune -f --all --volumes

	@if [ -n "$(shell docker volume ls -q)" ]; then \
		for volume in $(shell docker volume ls -q); do \
			docker volume rm $$volume 2>/dev/null || true; \
		done \
	fi

	docker network prune -f

	docker image prune -f

	@if [ -n "$(shell docker ps -aq)" ]; then \
		for container in $(shell docker ps -aq); do \
			docker rm $$container 2>/dev/null || true; \
		done \
	fi

# Display the status of all services
.PHONY: status
status:
	docker compose ps -a

.PHONY: info
info:
	docker ps -a

.PHONY: vbash
vbash:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: No container name provided."; \
		exit 1; \
	fi
	docker exec -it $(filter-out $@,$(MAKECMDGOALS)) bash -c '. venv/bin/activate && $$SHELL'

.PHONY: bash
bash:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: No container name provided."; \
		exit 1; \
	fi
	docker exec -it $(filter-out $@,$(MAKECMDGOALS)) bash

.PHONY: pytest-venv
pytest-venv:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: No container name provided."; \
		exit 1; \
	fi
	docker exec -it $(filter-out $@,$(MAKECMDGOALS)) bash -c '. venv/bin/activate && pytest -svv || echo "Pytest encountered an error"'


.PHONY: dlog
dlog:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: No container name provided."; \
		exit 1; \
	fi
	docker exec -it $(filter-out $@,$(MAKECMDGOALS)) bash -c 'cat /var/log/django_debug.log'

.PHONY: dlogerr
dlog-err:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: No container name provided."; \
		exit 1; \
	fi
	docker exec -it $(filter-out $@,$(MAKECMDGOALS)) bash -c 'cat /var/log/django_error.log'

.PHONY: clog
clog:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: No container name provided."; \
		exit 1; \
	fi
	docker exec -it $(filter-out $@,$(MAKECMDGOALS)) bash -c 'cat /var/log/consumer.log'

.PHONY: clog-err
clog-err:
	@if [ -z "$(filter-out $@,$(MAKECMDGOALS))" ]; then \
		echo "Error: No container name provided."; \
		exit 1; \
	fi
	docker exec -it $(filter-out $@,$(MAKECMDGOALS)) bash -c 'cat /var/log/consumer_err.log'


%:
	@:

# Display help
.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build and start all services"
	@echo "  build      - Build all services"
	@echo "  up         - Start all services"
	@echo "  down       - Stop all services"
	@echo "  re         - Restart all services"
	@echo "  logs       - Show logs for all services"
	@echo "  pull       - Pull latest images for all services"
	@echo "  clean      - Remove stopped containers and unused images, networks, and volumes"
	@echo "  status     - Display the status of all services"
	@echo "  info       - Display the status of all services"
	@echo "  bash       - Open a bash shell in a running container"
	@echo "  help       - Display this help message"
