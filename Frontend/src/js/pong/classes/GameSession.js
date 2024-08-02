// GameSession.js
import socket from '../socket.js';
import { initializeEventHandlers } from '../eventhandlers.js';
import { translateCoordinates } from '../utils.js';
import Paddle from './Paddle.js';
import Ball from './Ball.js';
import PlayingField from './PlayingField.js';
import { LEFT_PADDLE_START, RIGHT_PADDLE_START } from '../constants.js';

class GameSession {
    constructor() {
        this.gameId = null;
        this.player1Id = null;
        this.player2Id = null;
        this.localPlayerId = null;
        this.isRemote = false; // Flag to distinguish between remote and local multiplayer
        this.isLocalTournament = false; // Flag to distinguish between local tournament and regular game
        this.socket = socket;  // Attach the socket instance
        this.playingField = null;
        this.leftPaddle = null;
        this.rightPaddle = null;
        this.ball = null;
        this.player1Score = 0;
        this.player2Score = 0;
    }

    initialize(gameId, localPlayerId, player1Id, player2Id, isRemote, isLocalTournament, scene) {
        this.gameId = gameId;
        this.player1Id = player1Id;
        this.player2Id = player2Id;
        this.isRemote = isRemote;
        this.isLocalTournament = isLocalTournament;
        this.playingField = new PlayingField(scene);
        this.leftPaddle = new Paddle(scene, LEFT_PADDLE_START, 0x00ff00);
        this.rightPaddle = new Paddle(scene, RIGHT_PADDLE_START, 0xff0000);
        this.ball = new Ball(scene);
    
        this.playingField.addToScene();
        this.leftPaddle.addToScene();
        this.rightPaddle.addToScene();
        this.ball.addToScene();

        // Always connect to the server
        if (!this.socket.connected) {
            this.socket.connect();
        }
        let gameInitData = { 
            'type': 'start_game',
            'game_id': gameId,
            'local_player_id': localPlayerId,
            'player1_id': player1Id,
            'player2_id': player2Id,
            'is_remote': isRemote,
            'is_local_tournament': isLocalTournament,
        }
        console.log('Game Session Initialized');
        console.log('Game Init Data:', gameInitData);

        if (isRemote === false) {
            this.socket.emit('start_game', gameInitData);
        }
        else {
            this.socket.emit('join_game', gameInitData);
        }
        initializeEventHandlers(this);

    }

    sendMovement(data) {
        this.socket.emit('move_paddle', data);
    }

    handleGameStateUpdate(data) {
        const translatedData = translateCoordinates(data);
        this.leftPaddle.updatePosition(translatedData.player1_position);
        this.rightPaddle.updatePosition(translatedData.player2_position);
        this.ball.updatePosition(translatedData.ball);
    }

    handleScoreUpdate(data) {
        console.log('Received score update:', data);
        this.player1Score = data.player1_score;
        this.player2Score = data.player2_score;
    }

    endGame(data) {
        console.log('Game over!');
        console.log(data);
        if (this.isRemote) {
            if (data.winner_id === this.localPlayerId) {
                console.log('You win!');
            }
            else {
                console.log('You lose!');
            }
        }
        else { 
            if (this.isLocalTournament) {
                console.log('Tournament match over!');
                // at this point we send winner to the tournament logic
            }
            else {
                console.log('Local game over!');
            }
            if (data.winner_id === this.player1Id) {
                console.log('Player 1 wins!');
            }
            else {
                console.log('Player 2 wins!');
            }
        }
        
        this.disconnect();
    }
    
    disconnect() {
        if (this.socket.connected) {
            this.socket.disconnect();
            console.log('Disconnected from server');
        }
    }
}

export default GameSession;
