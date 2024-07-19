# User_service

The user service is responsible for creating, reading, updating and deleting user records. The user service receives the username, email and password then stores them in the User table. The username and email are unique and the password is hashed and write-only.

Upon GET,PUT and DELETE requests for a user record, the user service will retrieve the access token from the request header and send it to the profile service to check if the access token exists in the UserTokens table. If the access token exists, the user service will process the request for the user record if the user record exists in the User table.

## Docker container configuration

Every single REST API endpoint has their own database. The database is a PostgreSQL database. The database name for all the endpoints is `postgres`. The database user and password for all the endpoints is inside the env file. The database port for all the endpoints is `5432`.

The requirements package is inside the requirements.txt file.
The run_consumer.sh file is used to run the consumer.py file inside the user_management/user_management folder. The consumer.py file is used to consume the message from the RabbitMQ message broker and check if the username and password are correct.
The tools.sh and run_consumer.sh files are running inside the Docker container using the supervisord service. The supervisord service is used to run multiple services inside the Docker container.
The tools.sh file is used to run the init_database.sh file and run the API.
The API runs inside a virtual environment. The virtual environment is created inside the Docker container using command python3.12 -m venv venv. The virtual environment is activated using command source venv/bin/activate inside the tools.sh file.

The API runs on port 8000 and exposed to 8000.

## Tutorial to use the user_service

After running the makefile, you can access the API using the following url:

- `http://localhost:3000/user/register/` "create user record using POST method"
- `http://localhost:3000/user/` "List users records using GET method"
- `http://localhost:3000/user/<int:pk>/` "without angel brackets" "retrieve, update and delete user record using GET, PUT and DELETE methods respectively"
- `http://localhost:3000/user/login/` "login user using POST method"
- `http://localhost:3000/user/logout/` "logout user using POST method"
 - `"http://localhost:3000/user/<int:user_pk>/friends/"` "List friends of a user using GET method"
- `"http://localhost:3000/user/<int:user_pk>/request/<int:pk>/"` send friend request to a user using POST method or withdraw friend request
- `"http://localhost:3000/user/<int:user_pk>/accept/<int:pk>/"` accept friend request PUT method
- `"http://localhost:3000/user/<int:user_pk>/pending/"` "List pending friend requests of a user using GET method"
- `"http://localhost:3000/user/<int:user_pk>/reject/<int:pk>"` "Accept or reject friend request using PUT method"
- `"http://localhost:3000/user/<int:user_pk>/friends/<int:pk>/remove/"` "Remove friend using DELETE method"
You should send a JSON object with the following fields:

```JSON
{
    "username": "username",
    "email": "email",
    "password": "password"
}
```

The API will store the username, email and hashed password in the User table.
The username and email are unique.

The User table consists of the following fields:
You can find it in user_management/user_management/users/models.py

| Field Name | Data Type | Description                        |
| ---------- | --------- | ---------------------------------- |
| id         | Integer   | Primary Key                        |
| username   | String    | User Name                          |
| email      | String    | User Email                         |
| password   | String    | User Password (Password is hashed) |

Later I will limit the access to the API using nginx reverse proxy and only the frontend will be able to access the API.
