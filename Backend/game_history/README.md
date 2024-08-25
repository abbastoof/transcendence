## Game History Microservice Documentation

### Overview

The Game History microservice is a key component of the Transcendence project at 42 School. This service is responsible for recording and managing the history of ping pong games played by users. It supports creating, retrieving, updating, and deleting game history and game statistics records.

### Directory Structure

```
.
├── Dockerfile
├── game_history
│   ├── game_data
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── game_history
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_game_history.py
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

The `game_history` microservice is containerized using Docker. The `Dockerfile` sets up the environment needed to run the Django application.

#### Environment Variables

Environment variables should be defined in the `.env` file to configure the service. These may include database connection details, secret keys, and other configurations.

### Models

The `GameHistory` model represents a record of a game played between two users. It includes the following fields:

- `game_id`: AutoField, primary key.
- `player1_id`: Integer, ID of the first player.
- `player2_id`: Integer, ID of the second player.
- `winner_id`: Integer, ID of the winning player.
- `start_time`: DateTime, the start time of the game.
- `end_time`: DateTime, the end time of the game (optional).

The `GameStat` model represents the statistics of a game, linked to a `GameHistory` record. It includes the following fields:

- `game_id`: OneToOneField, primary key linked to `GameHistory`.
- `player1_score`: Integer, score of the first player.
- `player2_score`: Integer, score of the second player.
- `player1_hits`: Integer, number of hits by the first player.
- `player2_hits`: Integer, number of hits by the second player.
- `longest_rally`: Integer, the longest rally in the game.

### Serializers

- The `GameHistorySerializer` converts `GameHistory` model instances to JSON format and validates incoming data.
- The `GameStatSerializer` converts `GameStat` model instances to JSON format and validates incoming data.

### Views

- The `GameHistoryViewSet` handles the CRUD operations for game history records.
- The `GameStatViewSet` handles the CRUD operations for game statistics records.

### URLs

The microservice defines several endpoints to interact with the game history and game statistics data. These endpoints are defined in the `game_data/urls.py` file. Here is an overview of how to access them:

- **Game History Endpoints:**
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

- **Game Stat Endpoints:**
  - **List and Create Game Stat Records:**
    ```
    GET /game-stat/
    POST /game-stat/
    ```
  - **Retrieve, Update, and Delete a Specific Game Stat Record:**
    ```
    GET /game-stat/<int:pk>/
    PUT /game-stat/<int:pk>/
    DELETE /game-stat/<int:pk>/
    ```

### Tests

#### Directory Structure

The tests for the Game History microservice are located in the `game_history/game_history/tests/` directory. The tests ensure that the CRUD operations for game history and game statistics records are working correctly.

#### Test Cases

1. **Test Create Game History**
   - Verifies that a game history record can be created successfully.

2. **Test List Game Histories**
   - Verifies that a list of game history records can be retrieved successfully.

3. **Test Retrieve Game History**
   - Verifies that a specific game history record can be retrieved successfully.

4. **Test Update Game History**
   - Verifies that a specific game history record can be updated successfully.

5. **Test Delete Game History**
   - Verifies that a specific game history record can be deleted successfully.

6. **Test Create Game Stat**
   - Verifies that a game statistics record can be created successfully.

7. **Test List Game Stats**
   - Verifies that a list of game statistics records can be retrieved successfully.

8. **Test Retrieve Game Stat**
   - Verifies that a specific game statistics record can be retrieved successfully.

9. **Test Update Game Stat**
   - Verifies that a specific game statistics record can be updated successfully.

10. **Test Delete Game Stat**
    - Verifies that a specific game statistics record can be deleted successfully.

### Running Tests

To run the tests, use the following commands:

1. Build and start the Docker container:
   ```sh
   docker-compose up --build
   ```

2. Execute the tests within the Docker container:
   ```sh
   docker exec -it game-history bash
   . venv/bin/activate
   pytest
   ```

### Conclusion

The Game History microservice is an essential part of the Transcendence project, providing a robust solution for managing game history and game statistics records. This documentation provides an overview of the setup, implementation, and testing of the service. For further details, refer to the respective source code files in the project directory.
