# Token_service

The token service is responsible for generating the refresh and access tokens. The token service receives the username then generates the refresh and access tokens, You can achieve this through the login url in profile-service.
Also the token service is responsible for refreshing the access token.

## Docker container configuration

Every single REST API endpoint has their own database. The database is a PostgreSQL database. The database name for this endpoints is `token_service`. The database user and password for all the endpoints is inside the env file. The database port for all the endpoints is `5432`.
Every single REST API endpoint has their own database. The database is a PostgreSQL database. The database name for this endpoints is `token_service`. The database user and password for all the endpoints is inside the env file. The database port for all the endpoints is `5432`.

The requirements package is inside the requirements.txt file.
The tools.sh file is used to run the init_database.sh file and run the API.
The API runs inside a virtual environment. The virtual environment is created inside the Docker container using command python3.12 -m venv venv. The virtual environment is activated using command source venv/bin/activate inside the tools.sh file.

The API runs on port 8000 and exposed to 8001.

## Tutorial to use the token_service

There are three endpoints in the token_service. The endpoints are:
- `auth/token/refresh/` - This endpoint is used to refresh the access token. to refresh the access token you need to send a request to this endpoint with the refresh token in the request body. 
You should send the "user refresh token" in the header as brearer token and The request will be like this:

```json
{
    "id": "user_id",
}
```
It will return the new access token as a response.
```json
{
    "access": "new access token"
}
```

- `auth/token/gen-tokens/` - This endpoint is used to generate the refresh and access tokens.
- `auth/token/invalidate-tokens/` - This endpoint is used by user-service logout or delete user to invalidate the refresh and access tokens.
- `auth/token/validate-token/` - This endpoint is used to validate the access token. If you send a request from frontend to this API your request will be like this:
```json
{
    "id": "user_id",
    "access": "your access token",
    "is_frontend": true
}
```
## The UserTokens model

The UserTokens model is used to store the refresh and access tokens. The UserTokens model has the following fields:
| Field      | Type     | Description                   |
| ---------- | ---------| ----------------------------- |
| id         | Integer  | The id of the user token      |
| username   | String   | The username of the user      |
| token_data | JSON     | The refresh and access tokens |
