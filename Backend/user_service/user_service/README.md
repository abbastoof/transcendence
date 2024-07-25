## WebSocket Integration Documentation

### Overview

This document provides an overview of how WebSocket integration has been implemented in the Django project, enabling real-time online status updates and notifications. It includes information on the setup, testing, and how the frontend can access the WebSocket services.

### Backend Setup

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

The Docker setup included Redis and Nginx services:

```yaml
services:
  redis:
    image: redis
    container_name: redis
    networks:
      - transcendence_network

  nginx:
    # Nginx service definition
```

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
