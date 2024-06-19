# Tutorial to use the project

Until we find a solution for environment variables, you can use "sample env" file. rename it to ".env".

This project consists of two endpoints that allows users to view, add, update, and delete user records. The application is built using the Django framework in Python. Every endpoint is using Postgresql as a database and Django Rest Framework to serialize the data and return it in JSON format. 

The address of the first endpoint user_management API is 
`http://127.0.0.1:8000/user/register` "create user record using POST method"
`http://127.0.0.1:8000/user/` "retrieve all user records using GET method only super user or staff can access"
`http://127.0.0.1:8000/user/<int:pk>` "without angel brackets" "retrieve, update and delete user record using GET, PUT and DELETE methods respectively"

The address of the second endpoint user_auth API is `http://127.0.0.1:8000/auth/api/token/`

The first endpoint allows users to create a user, update, delete and retrieve. The token is valid for 60 minutes.

User table consists of the following fields:
You can find it in user_management/user_management/users/models.py

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| id         | Integer   | Primary Key |
| username   | String    | User Name   |
| email      | String    | User Email  |
| password   | String    | User Password (Password is hashed)|

The user_auth table consists of the following fields:

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| username   | String    | User Name   |
| token_data | JSON      | Token Data  |

token_data is a JSON object that consists of two dictionaries:
1. refresh: Refresh Token

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| token      | String    | Refresh Token |
| exp        | Integer   | Expiry Time   |

2. access: Access Token

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| token      | String    | Access Token |
| exp        | Integer   | Expiry Time  |


For now I have routed the user_management API to port 8000 and user_auth API to port 8001. The Rabbitmq management is routed to port 15672. You can change the port number in the docker-compose.yml file.
The address of all of them is `http://127.0.0.1` or `http://localhost`
