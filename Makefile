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
	docker compose up -d --build

# Stop all services
.PHONY: down
down:
	docker compose down -v

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
	docker system prune -f --all
	docker volume prune -f
	docker network prune -f


# # Free up the port if it's already allocated
# .PHONY: free-port
# free-port:
# 	@echo "Checking for allocated port 15672..."
# 	@PIDS=$$(lsof -ti:15672 || netstat -nlp | grep :15672 | awk '{print $$7}' | cut -d'/' -f1 || ss -tuln | grep :15672 | awk '{print $$6}' | cut -d',' -f2); \
# 	if [ -n "$$PIDS" ]; then \
# 		echo "Port 15672 is in use by PIDs $$PIDS. Attempting to free it..."; \
# 		echo "$$PIDS" | xargs kill -9; \
# 		echo "Port 15672 has been freed."; \
# 	else \
# 		echo "Port 15672 is not in use."; \
# 	fi

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
	@echo "  free-port  - Free up the port if it's already allocated"
	@echo "  status     - Display the status of all services"
	@echo "  help       - Display this help message"
