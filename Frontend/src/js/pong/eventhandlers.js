import socket from './socket';
import GameSession from './classes/GameSession';
import { cleanUpGame, endGame } from './pong.js';

let isConnected = false
// Initialize event handlers for the game
// This function should be called once when the game is loaded
// It sets up event listeners for the game
// When the server sends a message, the corresponding event handler is called
// The event handlers are responsible for updating the game state
// The game state is updated by calling methods on the GameSession object
// The GameSession object is responsible for updating the game state
// Rendering is done in animate function in pong.js based on game states in GameSession object
export const initializeEventHandlers = (gameSession) => {
    
    // Event handler for the socket connection
    socket.on('connect', () => {
        isConnected = true
        console.log('Connected to server');
    });

    // Event handler for the socket disconnection
    socket.on('disconnect', (reason) => {
        isConnected = false
        console.log(`Disconnected from server: ${reason}`);
    });

    // Event handler for the game start message
    // This message is sent by the server when the game is ready to start
    // The game session object is responsible for handling the game
    socket.on('game_start', (data) => {
        if (data && data.gameId) {
            if (data.gameId === gameSession.gameId) {
                gameSession.handleGameStart();
            }
            else {
                console.log('Received game start for different game, was ' + data.gameId + ', expected ' + gameSession.gameId);
            }
        }
    });
    socket.on('error', (error) => {
        gameSession.scoreBoard.showErrorText();
        setTimeout(() => {
            endGame();
        }, 2000);
    });
    
    socket.on('reconnect_error', (error) => {
        console.error('Reconnection error:', error);
    });
    // Event handler for the game state message
    // This message is sent by the server when the game state is updated
    // The game session object is responsible for updating the game state
    socket.on('send_game_state', (data) => {
        if (data && data.gameId) {
            if (data.gameId === gameSession.gameId) {
                gameSession.handleGameStateUpdate(data);
            } 
            else {
                console.log('Received game state for different game, was ' + data.game_id + ', expected ' + gameSession.gameId);
            }
        } else {
            console.log('game_id is undefined or data is malformed:', data);
        }
    });

    // Event handler for the score message
    // This message is sent by the server when the score is updated
    // The game session object is responsible for updating the score
    socket.on('score', (data) => {
        if (data && data.gameId) {
            if (data.gameId === gameSession.gameId) {
                gameSession.handleScoreUpdate(data);
            } 
            else {
                console.log('Received score update for different game, was ' + data.game_id + ', expected ' + gameSession.gameId);
            }
        } 
        else {
            console.log('game_id is undefined or data is malformed:', data);
        }
    });

    // Event handler for the quit game message
    // This message is sent by the server when a player quits the game
    // The game session object is responsible for handling the quit
    socket.on('quit_game', (data) => {
        if (data && data.game_id) {
            if (data.game_id === gameSession.gameId && gameSession.inProgress) {
                
                console.log(`Player ${data.quitting_player_id} has quit the game.`);
                gameSession.handleOpponentQuit(data);
            }
            else {
                console.log('Received quit game for different game, was ' + data.game_id + ', expected ' + gameSession.gameId);
            }
        }
    });

    socket.on('cancel_game', (data) => {
        if (data && data.gameId) {
            if (data.gameId === gameSession.gameId && gameSession.inProgress) {
                gameSession.inProgress = false;
                console.log(`Game ${data.gameId} has been cancelled.`);
                gameSession.handleCancelGame(data);
                setTimeout(() => {
                    endGame();
                }, 2000);
            }
            else {
                console.log('Received cancel game for different game, was ' + data.game_id + ', expected ' + gameSession.gameId);
            }
        }
        
    });

    // Event handler for the game over message
    // This message is sent by the server when the game is over
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

    // Set a flag to manage if the game is active

    window.addEventListener('beforeunload', (event) => {
    if (gameSession.inProgress === true) {
        // Notify the server that the player is quitting
        gameSession.quitGame();
        // Optionally, show a confirmation dialog (may not work in all browsers)
        event.preventDefault();
        return "Are you sure you want to leave the game?";
    }
    });
    // Add other event handlers as needed
    console.log('Event handlers initialized');

};

// Emit events to the server
export const sendMovement = (data) => {
    if (isConnected) {
        socket.emit('move_paddle', data);
    }
    else {
        console.log("cannot send anthing, not connected")
    }
};

// Send quit game message to the server
export const sendQuit = (gameId, playerId) => {
    socket.emit('quit_game', {game_id: gameId, player_id: playerId});
    console.log('Quit game message sent');
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
    socket.off('error');
    console.log('Event handlers removed');
};