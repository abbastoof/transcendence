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
	docker compose down --rmi all --volumes --remove-orphans

# Restart all services
.PHONY: re
re: down clean up

# Show logs for all services
.PHONY: logs
logs:
	docker compose logs -f

# Pull latest images for all services
.PHONY: pull
pull:
	docker compose pull

# Remove stopped containers and unused images, networks, and volumes
.PHONY: clean
clean:
	rm -rf /database_volume
	docker system prune -f --all --volumes
	docker volume prune -f
	docker network prune -f
	docker image prune -f
	@if [ -n "$(shell docker ps -aq)" ]; then \
		for container in $(shell docker ps -aq); do \
			docker rm $$container; \
		done \
	fi
	@if [ -n "$(shell docker volume ls -q)" ]; then \
		for volume in $(shell docker volume ls -q); do \
			docker volume rm $$volume; \
		done \
	fi

# Display the status of all services
.PHONY: status
status:
	docker compose ps

.PHONY: bvenv
bvenv:
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
	@echo "  help       - Display this help message"
