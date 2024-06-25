# Auth_service

This is a simple authentication service that uses JWT to authenticate users.

## Docker container configuration

Every single REST API endpoint has their own database. The database is a PostgreSQL database. The database name for all the endpoints is `postgres`. The database user and password for all the endpoints is inside the env file. The database port for all the endpoints is `5432`.

The requirements package is inside the requirements.txt file.
The tools.sh file is used to run the init_database.sh file and run the API.
The API runs inside a virtual environment. The virtual environment is created inside the Docker container using command python3.12 -m venv venv. The virtual environment is activated using command source venv/bin/activate inside the tools.sh file.

The API runs on port 8000 and exposed to 8001.

## Tutorial to use the auth_service

After running the makefile, you can access the API using the following url:

- `http://auth-service:8000/auth/api/token/`

You should send a JSON object with the following fields:

```JSON
{
    "username": "username",
    "password": "password"
}
```

The API will send the JSON object to the user_service API through the RabbitMQ message broker. The user_service API will check if the username and password are correct.
If the username and password are correct, the API will generate the refresh and access keys and return a JSON object with the following fields:

```JSON
{
    "refresh": "refresh token"
    "access": "access token"
}
```

The access token is valid for 60 minutes. The refresh token is valid for 24 hours. The username and Token Data are stored in the UserTokens table.

The UserTokens table consists of the following fields:

| Field Name | Data Type | Description |
| ---------- | --------- | ----------- |
| username   | String    | User Name   |
| token_data | JSON      | Token Data  |

token_data is a JSON object that consists of two dictionaries:

1. refresh: Refresh Token

| Field Name | Data Type | Description   |
| ---------- | --------- | ------------- |
| token      | String    | Refresh Token |
| exp        | Integer   | Expiry Time   |

2. access: Access Token

| Field Name | Data Type | Description  |
| ---------- | --------- | ------------ |
| token      | String    | Access Token |
| exp        | Integer   | Expiry Time  |

Later I will limit the access to the API using nginx reverse proxy and only the frontend will be able to access the API.
