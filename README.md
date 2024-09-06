### Ft_transcendence
This project is our final project of core studies in Hive Helsinki coding school. It's a website that allows users to play the game of pong against each other. The game is played in real time, and the users can sucscribe to the website. The project is divided into two parts: the game server and the web server. The game server is responsible for managing the games and the web server is responsible for managing the users and user game history. The project is written in HTML, bootstrap, Javascript, Python, Django rest framework and uses a PostgreSQL database. The game server uses socket.io the real-time communication between the users.
All the project is dockerized and uses docker-compose to run the project.

## Installation
To run the project, you need to have docker and docker-compose installed on your machine. You can install docker and docker-compose by following the instructions on the official docker website. Once you have docker and docker-compose installed, you can clone the project and run the following command in the root directory of the project:
```bash
cp sample\ env .env
```
This command will create a .env file in the root directory of the project. You can change the values of the variables in the .env file to suit your needs.
You should set the value of the `HOSTNAME` variable to the IP address or hostname of your machine. You can get the IP address of your machine by running the following command:
```bash
hostname -I | awk '{print "IP " $1}' # for linux users to get the IP address 
hostname # for mac or linux users to get the hostname
USER_SERVICE_EMAIL = 'add your email' # This email will be used by app to send otp to the user email
USER_SERVICE_PASS = 'add your email password'
```
You don't have to set the other values of the variables in the .env file. The default values should work fine. Once you have set the values of the variables in the .env file, you can run the following command in the root directory of the project:
```bash
make
```
This command will build the docker images and run the project. 
Now you can access the website by going to the following URL in your browser:
```
https://<HOSTNAME>:3000
```
You can replace `<HOSTNAME>` with the IP address or hostname of your machine that you got set earlier in the .env file. You should see the website now. You can create an account and start playing the game of pong.
## Note
For online play need to have two registered users and one of them should create a game and can join the game by clicking on online play.

You can find more information about the project in the README.md file in the backend directory of the project. every microservice has its own README.md file in its directory.
