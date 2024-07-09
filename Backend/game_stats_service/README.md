## Game Stats Service Microservice Documentation

### Overview

The Game Stats Service microservice is a crucial part of the Transcendence project at 42 School. This service is designed to handle the recording and management of game statistics for ping pong games played by users. It includes capabilities for creating, retrieving, updating, and deleting game statistics records.

### Directory Structure

```
.
├── Dockerfile
├── game_stats_service
│   ├── game_stats
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── game_stats_service
│   │   ├── asgi.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── tests
│   │   │   ├── conftest.py
│   │   │   ├── __init__.py
│   │   │   └── test_game_stats_service.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── manage.py
├── init_database.sh
├── requirements.txt
├── supervisord.conf
└── tools.sh
```

### Setup

#### Docker Setup

The `game_stats_service` microservice is containerized using Docker. The `Dockerfile` sets up the environment required to run the Django application.

### Models

The `GameHistory` model represents a record of a game, including details like players, winner, and game timing.

### Serializers

The `GameHistorySerializer` converts model instances to JSON format and validates incoming data.

### Views

The `GameHistoryViewSet` manages CRUD operations for game history records.

### URLs

The microservice defines several endpoints to interact with game history data, specified in the `game_stats/urls.py` file.

- **List and Create Game History Records:**
  ```
  GET /game-history/
  POST /game-history/
  ```
- **Retrieve, Update, and Delete a Specific Game History Record:**
  ```
  GET /game-history/<int:pk>/
  PUT /game-history/<int:pk>/
  DELETE /game-history/<int:pk>/
  ```

### Tests

#### Directory Structure

The tests for the Game Stats Service microservice are located in the `game_stats_service/game_stats_service/tests/` directory. These tests verify the correct functioning of CRUD operations.

#### Test Cases

1. **Test Create Game History**
2. **Test List Game Histories**
3. **Test Retrieve Game History**
4. **Test Update Game History**
5. **Test Delete Game History**
6. **Test Create Game History Validation Error**

### Running Tests

To run the tests, follow these steps:

1. Ensure the Docker containers are up and running:
   ```sh
   docker-compose up --build
   ```

2. Access the `game-stats-service` container:
   ```sh
   docker exec -it game-stats-service bash
   ```

3. Activate the virtual environment and run the tests:
   ```sh
   . venv/bin/activate
   pytest
   ```

### Conclusion

The Game Stats Service microservice is an essential component of the Transcendence project, offering robust functionality for managing game statistics. This documentation provides an overview of the setup, implementation, and testing of the service. For further details, refer to the respective source code files in the project directory.
