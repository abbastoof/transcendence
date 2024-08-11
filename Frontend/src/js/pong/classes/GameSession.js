// GameSession.js
import socket from '../socket.js';
import { initializeEventHandlers } from '../eventhandlers.js';
import { translateCoordinates } from '../utils.js';
import Paddle from './Paddle.js';
import Ball from './Ball.js';
import PlayingField from './PlayingField.js';
import ScoreBoard from './ScoreBoard.js';
import { LEFT_PADDLE_START, RIGHT_PADDLE_START } from '../constants.js';
import { changeCameraAngle, endGame } from '../pong.js';
import { globalState } from '../globalState.js';

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
        this.onGameEndCallback = null;
        this.scoreBoard = null;
        this.dataSent = false;
        this.player1Alias = "Player1"
        this.player2Alias = "Player2"
    }

    initialize(gameId, localPlayerId, player1Id, player2Id, isRemote, isLocalTournament, scene, onGameEnd) {
        this.gameId = gameId;
        this.player1Id = player1Id;
        this.player2Id = player2Id;
        this.isRemote = isRemote;
        this.isLocalTournament = isLocalTournament;
        if (isLocalTournament === true) {
            const tournamentPlayers = JSON.parse(localStorage.getItem('tournamentPlayers'));
            this.player1Alias = tournamentPlayers[player1Id - 1].name 
            this.player2Alias = tournamentPlayers[player2Id - 1].name
        }
        this.onGameEndCallback = typeof onGameEnd === 'function' ? onGameEnd : null; // Ensure it's a function
        this.playingField = new PlayingField(scene, gameId, player1Id, player2Id);
        this.leftPaddle = new Paddle(scene, LEFT_PADDLE_START, 0xffff00);
        this.rightPaddle = new Paddle(scene, RIGHT_PADDLE_START, 0xff0000);
        this.ball = new Ball(scene);
        this.scoreBoard = new ScoreBoard(scene);
        const player1Text = `${this.player1Alias} ${this.player1Score}`;
        const player2Text = `${this.player2Alias} ${this.player2Score}`;
        this.scoreBoard.createScoreBoard(player1Text, player2Text);
        console.log("Type of onGameEndCallback:", typeof this.onGameEndCallback);

        this.playingField.addToScene();
        this.leftPaddle.addToScene();
        this.rightPaddle.addToScene();
        this.ball.addToScene();

        // Always connect to the server
        if (!this.socket.connected) {
            this.socket.connect();
        }
        let gameInitData = { 
            'type': null,
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
            gameInitData['type'] = 'start_game';
            this.socket.emit('start_game', gameInitData);
        }
        else {
            gameInitData['type'] = 'join_game';
            this.socket.emit('join_game', gameInitData);
        }
        initializeEventHandlers(this);

    }

    sendMovement(data) {
        this.socket.emit('move_paddle', data);
    }

    handleGameStateUpdate(data) {
        const translatedData = translateCoordinates(data);
        if (this.isRemote && (this.localPlayerId !== this.player1Id)) {
            this.leftPaddle.updatePosition(translatedData.player2Pos);
            this.rightPaddle.updatePosition(translatedData.player1Pos);
        }
        else {
            this.leftPaddle.updatePosition(translatedData.player1Pos);
            this.rightPaddle.updatePosition(translatedData.player2Pos);
        }
        this.ball.updatePosition(translatedData.ball);
        if (data.ballDelta.dx > 0  && globalState.playingFieldMaterial !==  null) {
            globalState.playingFieldMaterial.uniforms.ballDx.value = 1.0;
        }
        else if (globalState.playingFieldMaterial !==  null) {
            globalState.playingFieldMaterial.uniforms.ballDx.value = -1.0;
        }
        if (data.bounce === true) {
            console.log('Bounce detected');
            globalState.rgbShift.enabled = true;
            globalState.rgbShift.uniforms.amount.value = 0.015;
            if (Math.random() < 0.5) {
                globalState.glitchPass.enabled = true;
            }
        }
        else {
            globalState.rgbShift.enabled = false;
            globalState.glitchPass.enabled = false;
            globalState.rgbShift.uniforms.amount.value = 0.0;
        }
    }

    handleScoreUpdate(data) {
        this.scoreBoard.showGoalText();
        this.player1Score = data.player1Score;
        this.player2Score = data.player2Score;
        setTimeout(() => {
            this.scoreBoard.updateScores(this.player1Alias, this.player1Score, this.player2Alias, this.player2Score);
        }, 2000);
    }

    handleGameOver(data) {
        //globalState.playingFieldMaterial.uniforms.ballDx.value = 0.1;
        this.leftPaddle.removeFromScene();
        this.rightPaddle.removeFromScene();
        //changeCameraAngle();
        this.disconnect();
        setTimeout(() => {
        if (typeof this.onGameEndCallback === 'function') {
            if (this.dataSent === false) {
                
                endGame();
                this.onGameEndCallback(data);
                console.log("Game end callback executed, forwarded data: ", data);
                this.dataSent = true;
            }
            else {
                console.log("Game end callback already executed.");
            }
        }
        else {
            console.log("No game end callback defined.");
        }
        }, 3000);
    }
    
    
    disconnect() {
        if (this.socket.connected) {
            this.socket.disconnect();
            console.log('Disconnected from server');
        }
    }
}

export default GameSession;
