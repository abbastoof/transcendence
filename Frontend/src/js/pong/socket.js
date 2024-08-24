import { io } from 'socket.io-client';

// Use the proxy path for local development
const socket = io('/', {path: '/game-server/socket.io',
    pingInterval: 10000,  // 10 seconds between pings
    pingTimeout: 5000     // 5 seconds to wait for pong before disconnecting
});
// const socket = io();

// socket.on('connect', () => {
//     console.log('Connected to game server');
// });

// socket.on('disconnect', () => {
//     console.log('Disconnected from game server');
// });

// socket.on('connect_error', (error) => {
//     console.error('Connection error:', error);
// });

export default socket;
