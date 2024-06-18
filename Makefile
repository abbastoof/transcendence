# Makefile for Docker Compose operations

# Define the name of the Docker Compose file
COMPOSE_FILE = docker-compose.yml

# Default target
.PHONY: all
all: up

# Build all services
.PHONY: build
build:
	docker-compose -f $(COMPOSE_FILE) build

# Start all services
.PHONY: up
up:
	docker-compose -f $(COMPOSE_FILE) up -d --build

# Stop all services
.PHONY: down
down:
	docker-compose -f $(COMPOSE_FILE) down

# Restart all services
.PHONY:  re
re: down up

# Show logs for all services
.PHONY: logs
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

# Pull latest images for all services
.PHONY: pull
pull:
	docker-compose -f $(COMPOSE_FILE) pull

# Remove stopped containers and unused images, networks, and volumes
.PHONY: clean
clean:
	docker system prune -f --all
	docker volume prune -f
	docker network prune -f

# Display the status of all services
.PHONY: status
status:
	docker-compose -f $(COMPOSE_FILE) ps

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
