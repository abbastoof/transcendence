import { PADDLE_SPEED } from './constants.js';
import { endGame } from './pong.js';
import { globalState } from './globalState.js';

// keys object to store the state of the keys
const keys = {};
let keydownHandler;
let keyupHandler;

export function initializeControls(){

    keydownHandler = (event) => {
        keys[event.key] = true;
    };

    keyupHandler = (event) => {
        keys[event.key] = false;
    };

    document.addEventListener('keydown', keydownHandler);
    document.addEventListener('keyup', keyupHandler);
}

export function clearControls(){
    // Remove keydown and keyup event listeners
    if (keydownHandler) {
        document.removeEventListener('keydown', keydownHandler);
        keydownHandler = null;
    }

    if (keyupHandler) {
        document.removeEventListener('keyup', keyupHandler);
        keyupHandler = null;
    }
}

// Function to handle the game controls
export function localGameControls(gameSession) {
    let leftDeltaZ = 0;
    let rightDeltaZ = 0;
    if (gameSession.inProgress === false) {
        return;
    }
    if ((keys['w'] || keys['W']) && !gameSession.leftPaddle.intersectsWall(gameSession.playingField.upperWall.boundingBox)) {
        leftDeltaZ -= PADDLE_SPEED;
    }
    if ((keys['s'] || keys['S']) && !gameSession.leftPaddle.intersectsWall(gameSession.playingField.lowerWall.boundingBox)) {
        leftDeltaZ += PADDLE_SPEED;
    }
    if ((keys['ArrowUp']) && !gameSession.rightPaddle.intersectsWall(gameSession.playingField.upperWall.boundingBox)) {
        rightDeltaZ -= PADDLE_SPEED;
    }
    if ((keys['ArrowDown']) && !gameSession.rightPaddle.intersectsWall(gameSession.playingField.lowerWall.boundingBox)) {
        rightDeltaZ += PADDLE_SPEED;
    }
    gameSession.leftPaddle.move(leftDeltaZ)
    gameSession.rightPaddle.move(rightDeltaZ);

    if (leftDeltaZ !== 0 || rightDeltaZ !== 0) {
        let emitData = {
            'type': 'move_paddle',
            'game_id': gameSession.gameId,
            'player1_id': gameSession.player1Id, 
            'p1_delta_z': leftDeltaZ,
            'player2_id': gameSession.player2Id,
            'p2_delta_z': rightDeltaZ
        };
    gameSession.sendMovement(emitData);
    }
}

// Function to handle the remote game controls
export function remoteGameControls(gameSession) {
    let deltaZ = 0;
    
    if (gameSession.inProgress === false) {
        return;
    }
    if ((keys['q'])) {
        gameSession.quitGame();
    }
    let playerPaddle;
    if (globalState.invertedView)
        playerPaddle = gameSession.rightPaddle;
    else
        playerPaddle = gameSession.leftPaddle;
    // Capture input for the local player’s paddle

    if (globalState.invertedView) {
        if ((keys['s'] || keys['S']) && !playerPaddle.intersectsWall(gameSession.playingField.upperWall.boundingBox)) {
            deltaZ -= PADDLE_SPEED;
        }
        else if ((keys['w'] || keys['W']) && !playerPaddle.intersectsWall(gameSession.playingField.lowerWall.boundingBox)){
            deltaZ += PADDLE_SPEED;
        }
        //deltaZ *= -1
    }
    else {
        if ((keys['w'] || keys['W']) && !playerPaddle.intersectsWall(gameSession.playingField.upperWall.boundingBox)) {
            deltaZ -= PADDLE_SPEED;
        }
        else if ((keys['s'] || keys['S']) && !playerPaddle.intersectsWall(gameSession.playingField.lowerWall.boundingBox)){
            deltaZ += PADDLE_SPEED;
        }
    }
    playerPaddle.move(deltaZ)
   if (deltaZ !== 0) {
        let emitData = {
            'type': 'move_paddle',
            'game_id': gameSession.gameId,
            'player_id': gameSession.localPlayerId,
            'delta_z': deltaZ
        };
        gameSession.sendMovement(emitData);
    }
}

