# Makefile for Docker Compose operations

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
	sudo rm -rf /database_volume
	docker system prune -f --all
	docker volume prune -f
	docker network prune -f

# Display the status of all services
.PHONY: status
status:
	docker compose ps

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
