import socket from './socket';
import GameSession from './classes/GameSession';
import ScoreBoard from './classes/ScoreBoard.js';
import { cleanUpGame, endGame } from './pong.js';

let isConnected = false;
let beforeUnloadHandler;

// Initialize event handlers for the game
export const initializeEventHandlers = (gameSession) => {
    // Event handler for the socket connection
    socket.on('connect', () => {
        isConnected = true;
    });

    // Event handler for the socket disconnection
    socket.on('disconnect', (reason) => {
        isConnected = false;
        if (reason !== 'io client disconnect') {
            gameSession.handleError('Disconnected from server. Exiting game..');
        }
    });

    // Event handler for the game start message
    socket.on('game_start', (data) => {
        try {
            if (data && data.gameId) {
                if (data.gameId === gameSession.gameId) {
                    gameSession.handleGameStart();
                } 
            }
        } catch (error) {
            console.error('Error handling game_start:', error);
        }
    });

    // General error handler
    socket.on('error', (error) => {
        gameSession.handleError('An error occurred. Exiting game..');
    });

    // Event handler for the game state message
    socket.on('send_game_state', (data) => {
        try {
            if (data && data.gameId) {
                if (data.gameId === gameSession.gameId) {
                    gameSession.handleGameStateUpdate(data);
                }
            }
        } catch (error) {
            console.error('Error handling send_game_state:', error);
        }
    });

    // Event handler for the score message
    socket.on('score', (data) => {
        try {
            if (data && data.gameId) {
                if (data.gameId === gameSession.gameId) {
                    gameSession.handleScoreUpdate(data);
                }
            }
        } catch (error) {
            console.error('Error handling score update:', error);
        }
    });

    // Event handler for the quit game message
    socket.on('quit_game', (data) => {
        try {
            if (data && data.gameId) {
                if (data.gameId === gameSession.gameId && gameSession.inProgress) {
                    console.info(`Player ${data.quittingPlayerId} has quit the game.`);
                    gameSession.handleOpponentQuit(data);
                } 
            }
        } catch (error) {
            console.error('Error handling quit_game:', error);
        }
    });

    // Event handler for the cancel game message
    socket.on('cancel_game', (data) => {
        try {
            if (data && data.gameId) {
                if (data.gameId === gameSession.gameId) {
                    gameSession.inProgress = false;
                    gameSession.handleCancelGame(data);
                    setTimeout(() => {
                        endGame();
                    }, 2000);
                } 
            }
        } catch (error) {
            console.error('Error handling cancel_game:', error);
        }
    });

    // Event handler for the game over message
    socket.on('game_over', (data) => {
        try {
            if (data && data.game_id) {
                if (data.gameId === gameSession.game_id) {
                    gameSession.handleGameOver(data);
                } 
            }
        } catch (error) {
            console.error('Error handling game_over:', error);
        }
    });

    // Event handler for invalid token message
    socket.on('invalid_token', (data) => {
        gameSession.handleError('Invalid token. Exiting game..');
    });

    // Handle window unload
    // Define the beforeunload event handler
    beforeUnloadHandler = (event) => {
        if (gameSession.inProgress) {
            event.preventDefault();
            gameSession.quitGame();
            return 'Are you sure you want to leave the game?';
        }
    };

    window.addEventListener('beforeunload', beforeUnloadHandler);
};

// Emit events to the server
export const sendMovement = (data) => {
    if (isConnected) {
        socket.emit('move_paddle', data);
    } else {
        console.warn('Cannot send anything, not connected.');
    }
};

// Send quit game message to the server
export const sendQuit = (gameId, playerId) => {
    socket.emit('quit_game', { 'game_id': gameId, 'player_id': playerId });
};

// Cleanup function to remove event listeners
export const cleanupEventHandlers = () => {
    socket.off('connect');
    socket.off('disconnect');
    socket.off('game_start');
    socket.off('send_game_state');
    socket.off('score');
    socket.off('game_over');
    socket.off('quit_game');
    socket.off('cancel_game');
    socket.off('error');
    socket.off('invalid_token');
    if (beforeUnloadHandler) {
        window.removeEventListener('beforeunload', beforeUnloadHandler);
        beforeUnloadHandler = null; // Clear the handler reference
    }
};
