import socket from './socket';
import GameSession from './classes/GameSession';
import { endGame } from './pong.js';

export const initializeEventHandlers = (gameSession) => {
    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    socket.on('send_game_state', (data) => {
        if (data && data.game_id) {
            if (data.game_id === gameSession.gameId) {
                gameSession.handleGameStateUpdate(data);
            } 
            // else {
            //     console.log('Received game state for different game, was ' + data.game_id + ', expected ' + gameSession.gameId);
            // }
        } else {
            console.log('game_id is undefined or data is malformed:', data);
        }
});
    socket.on('score', (data) => {
        if (data && data.game_id) {
            if (data.game_id === gameSession.gameId) {
                gameSession.handleScoreUpdate(data);
            } 
            // else {
            //     console.log('Received score update for different game, was ' + data.game_id + ', expected ' + gameSession.gameId);
            // }
        } 
        else {
            console.log('game_id is undefined or data is malformed:', data);
        }
    });

    socket.on('game_over', (data) => {
        if (data && data.game_id) {
            if (data.game_id === gameSession.gameId) {
                gameSession.handleGameOver(data);
            } 
            else {
                console.log('Received game over for different game, was ' + data.game_id + ', expected ' + gameSession.gameId);
            }
        }
    });

    // Add other event handlers as needed
    console.log('Event handlers initialized');
};

// Emit events to the server
export const sendMovement = (data) => {
    socket.emit('move_paddle', data);
};
