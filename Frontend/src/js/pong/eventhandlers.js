import socket from './socket';
import GameSession from './classes/GameSession';

export const initializeEventHandlers = (gameSession) => {
    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    socket.on('send_game_state', (data) => {
        gameSession.handleGameStateUpdate(data);
    });

    socket.on('game_over', (data) => {
        console.log('Game over!');
        console.log(data);
    });

    // Add other event handlers as needed
    console.log('Event handlers initialized');
};

// Emit events to the server
export const sendMovement = (data) => {
    socket.emit('move_paddle', data);
};
