# User_service

The user service is responsible for creating, reading, updating and deleting user records. The user service receives the username, email and password then stores them in the User table. The username and email are unique and the password is hashed and write-only.

Upon GET,PUT and DELETE requests for a user record, the user service will retrieve the access token from the request header and send it to the profile service to check if the access token exists in the UserTokens table. If the access token exists, the user service will process the request for the user record if the user record exists in the User table.

## Docker container configuration

Every single REST API endpoint has their own database. The database is a PostgreSQL database. The database name for this endpoints is `user_service`. The database user and password for all the endpoints is inside the env file. The database port for all the endpoints is `5432`.

The requirements package is inside the requirements.txt file.
The tools.sh file is used to run the API.
The API runs inside a virtual environment. The virtual environment is created inside the Docker container using command python3.12 -m venv venv. The virtual environment is activated using command source venv/bin/activate inside the tools.sh file.

The API runs on port 8000.

## Tutorial to use the user_service

After running the makefile, you can access the API using the following url:

- `http://localhost:3000/user/register/` "create user record using POST method"
You should send a JSON object with the following fields:

```JSON
{
    "username": "username",
    "email": "email",
    "password": "password"
}
```

- `http://localhost:3000/user/` "List users records using GET method"
- `http://localhost:3000/user/<int:pk>/` "without angel brackets" "retrieve, update and delete user record using GET, PUT and DELETE methods respectively"
You can enable otp by sending a JSON object with the following fields:
```JSON
{
    "otp_status": "True"
}
```
- `http://localhost:3000/user/login/` "login user using POST method"
- `http://localhost:3000/user/verifyotp/` "send user otp using POST method"
You should send a JSON object with the following fields:
```JSON
{
    "username": "username",
    "password": "password",
    "otp": "otp"
}
```
- `http://localhost:3000/user/logout/` "logout user using POST method"
- `http://localhost:3000/user/<int:user_pk>/friends/` "List friends of a user using GET method"
The endpoint will return value is a JSON object with the following fields:
```JSON
[
    {
        "id": "id",
        "username": "xxx",
        "status": "status"
    }
]
```
- `http://localhost:3000/user/<int:user_pk>/request/` send friend request to a user in a JSON object using POST method the JSON object should contain the following fields:
```JSON
{
    "username": "username"
}
```
- `http://localhost:3000/user/<int:user_pk>/accept/<int:pk>/` accept friend request PUT method
- `http://localhost:3000/user/<int:user_pk>/pending/` "List pending friend requests of a user using GET method"
The endpoint will return value is a JSON object with the following fields:
```JSON
[
    {
        "sender_id": "id",
        "sender_username": "xxx",
        "receiver_id": "id",
        "receiver_username": "xxx",
        "status": "status"
    }
]
```
- `http://localhost:3000/user/<int:user_pk>/reject/<int:pk>/` "Accept or reject friend request using PUT method"
- `http://localhost:3000/user/<int:user_pk>/friends/<int:pk>/remove/` "Remove friend using DELETE method"


The API will store the username, email and hashed password in the User table.
The username and email are unique.

The User table consists of the following fields:
You can find it in user_management/user_management/users/models.py

| Field Name      | Data Type | Description                        |
| --------------- | --------- | ---------------------------------- |
| id              | Integer   | Primary Key                        |
| username        | String    | User Name                          |
| email           | String    | User Email                         |
| password        | String    | User Password (Password is hashed) |
| friends         | ManyToMany| Friends of the user                |
| avatar          | Image     | User Avatar                        |
| otp_status      | Boolean   | OTP Status                         |
| otp             | Integer   | OTP                                |
| otp_expiry_time | DateTime  | OTP Expiry Time                    |

Later I will limit the access to the API using nginx reverse proxy and only the frontend will be able to access the API.

## WebSocket Integration Documentation

### Overview

This document provides an overview of how WebSocket integration has been implemented in the Django project, enabling real-time online status updates and notifications. It includes information on the setup, testing, and how the frontend can access the WebSocket services.

### Backend Setup

## GameRoom model
The GameRoom model is used to store the game room information. The GameRoom model consists of the following fields:

| Field Name | Data Type                   | Description |
| ---------- | --------------------------- | ----------- |
| room_name  | String                      | Room Name   |
| player1    | ForeignKey from UserProfile | Player 1    |
| player2    | ForeignKey from UserProfile | Player 2    |

#### Dependencies

Django Channels and Redis were installed:

```bash
pip install channels
pip install channels-redis
```

#### Project Configuration

- **`settings.py`:**

  `channels` was added to `INSTALLED_APPS` and the channel layers were configured with Redis:

  ```python
  INSTALLED_APPS = [
      # other apps
      'channels',
  ]

  ASGI_APPLICATION = 'your_project_name.asgi.application'

  CHANNEL_LAYERS = {
      "default": {
          "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
          "CONFIG": {
              "hosts": [{
                  "address": "redis://redis:6379",
                  "ssl_cert_reqs": None,
              }],
          },
      },
  }
  ```

- **`asgi.py`:**

  `asgi.py` was set up to handle WebSocket connections:

  ```python
  import os
  from django.core.asgi import get_asgi_application
  from channels.routing import ProtocolTypeRouter, URLRouter
  from channels.auth import AuthMiddlewareStack
  import user_app.routing

  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

  application = ProtocolTypeRouter({
      'http': get_asgi_application(),
      'websocket': AuthMiddlewareStack(
          URLRouter(
              user_app.routing.websocket_urlpatterns
          )
      )
  })
  ```

- **`routing.py`:**

  WebSocket URL patterns were defined:

  ```python
  from django.urls import re_path
  from . import consumers

  websocket_urlpatterns = [
      re_path(r'ws/notify/', consumers.NotificationConsumer.as_asgi()),
      re_path(r'ws/online/', consumers.OnlineStatusConsumer.as_asgi()),
      re_path(r'ws/<int:id>/', consumers.PersonalChatConsumer.as_asgi()),
  ]
  ```

#### Nginx Configuration

Nginx was set up to support WebSocket connections. The `nginx.conf` was updated:

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 443 ssl;
    # other configurations

    location /ws/ {
        proxy_pass http://websocket-service;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Docker Configuration

The Docker setup included Redis service:

```yaml
services:
  redis:
    image: redis
    container_name: redis
    networks:
      - transcendence_network

### Testing WebSocket Connections

#### Using Postman

1. **Connect to WebSocket:**

   - Open Postman.
   - Select "New" -> "WebSocket Request".
   - Enter the WebSocket URL: `ws://127.0.0.1:3000/ws/online/`.

2. **Send Messages:**

   - Use the JSON format to send messages:
     ```json
     {
         "username": "example_user",
         "type": "open"
     }
     ```
   - To close the connection:
     ```json
     {
         "username": "example_user",
         "type": "close"
     }
     ```

### Frontend Access

To integrate WebSocket connections in the frontend, follow these steps:

1. **Connect to WebSocket:**

   Use JavaScript to create a WebSocket connection:

   ```javascript
   const socket = new WebSocket('ws://127.0.0.1:3000/ws/online/');

   socket.onopen = function(event) {
       console.log('WebSocket is connected.');
       socket.send(JSON.stringify({
           username: 'example_user',
           type: 'open'
       }));
   };

   socket.onmessage = function(event) {
       const data = JSON.parse(event.data);
       console.log('Message from server ', data);
   };

   socket.onclose = function(event) {
       console.log('WebSocket is closed now.');
   };

   socket.onerror = function(error) {
       console.log('WebSocket Error: ' + error);
   };
   ```

2. **Handling WebSocket Events:**

   Handle WebSocket events to update the frontend UI accordingly. For example:

   ```javascript
   socket.onmessage = function(event) {
       const data = JSON.parse(event.data);
       if (data.online_status !== undefined) {
           updateUserStatus(data.username, data.online_status);
       }
   };

   function updateUserStatus(username, status) {
       const userElement = document.getElementById(username);
       if (userElement) {
           userElement.className = status ? 'online' : 'offline';
       }
   }
   ```

### Summary

The setup included configuring Django Channels, Redis, and Nginx to support WebSocket connections. The frontend can connect to the WebSocket service and handle events to provide real-time updates to users.


