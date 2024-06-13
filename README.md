This project consists of two endpoints that allows users to view, add, update, and delete user records. The application is built using the Django framework in Python. Every endpoint is using Postgresql as a database and Django Rest Framework to serialize the data and return it in JSON format. 

The address of the first endpoint user_management API is http://127.0.0.1:8000/user/register and http://127.0.0.1:8000/user/<int:pk> "without angel brackets" for the second address.

The first endpoint allows users to login and receive a token that is used to authenticate the user. The token is valid for 60 minutes. The token is used to authenticate the user when they want to edit, update, or delete user records. The token is also used to authenticate the user when they want to view user records.
