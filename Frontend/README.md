### How to Run Frontend Container in Dev Mode with Hot Reload

1. Ensure your `.env` file includes the following lines (use the `sample env` as your `.env` file):

```bash
TARGET=development
NODE_ENV=development

.. rest of the .env file
```

2. Build the project:

```bash
make up
```

3. Once the containers have been created, check the logs of the `frontend` container:

```bash
docker compose logs frontend
```

Initially, the logs will show that the `frontend` container is waiting for the `user-service` to start. You should see something like this:

```bash
frontend  | Waiting for Django server at http://user-service:8001/user/register/...
```

Once the required backend services are running, the logs will display:

```bash
frontend  | Starting development server
frontend  |   VITE v5.3.4  ready in 224 ms
frontend  | 
frontend  |   ➜  Local:   http://localhost:3001/
frontend  |   ➜  Network: http://this.would.be.an.ip.address:3001/
```

4. Ctrl+click on the network IP address or copy the URL to your browser. Voilá! Hot reload should work, so when you change an HTML or JS file, the changes will update immediately as the server reloads. You won't need to restart or rebuild the service every time.

### How to Run Production Build

By default, the app will build in the production environment. To do this, comment out the environment variables in the `.env` file 

```bash
# TARGET=development
# NODE_ENV=development

.. rest of the .env file
```

Build the app

```bash
make up
```

Frontend will wait until backend services are started, but once that is done you can access the app at ```https://localhost:3000```