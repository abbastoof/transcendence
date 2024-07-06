# Token_service

The token service is responsible for generating the refresh and access tokens. The token service receives the username then generates the refresh and access tokens, You can achieve this through the login url in profile-service.
Also the token service is responsible for refreshing the access token.

## Docker container configuration

Every single REST API endpoint has their own database. The database is a PostgreSQL database. The database name for all the endpoints is `postgres`. The database user and password for all the endpoints is inside the env file. The database port for all the endpoints is `5432`.

The requirements package is inside the requirements.txt file.
The tools.sh file is used to run the init_database.sh file and run the API.
The API runs inside a virtual environment. The virtual environment is created inside the Docker container using command python3.12 -m venv venv. The virtual environment is activated using command source venv/bin/activate inside the tools.sh file.

The API runs on port 8000 and exposed to 8001.

## Tutorial to use the token_service

You can use the token_service by sending a POST request to the https://localhost:3000/auth/token/refresh/ endpoint with the refresh token in the header as a Bearer token and it will return a new access token.

