// pong.js
import * as bootstrap from 'bootstrap';
import GameSession from './classes/GameSession.js';
import { PADDLE_SPEED } from './constants.js';
import { init } from './init.js';
import { randFloat } from 'three/src/math/MathUtils.js';
import { globalState } from './globalState.js';
let gameStarted = false;
let gameSession, renderer, scene, camera, composer, animationId;

function callBackTestFunction(data) {
    console.log(data);
    console.log("callback called back");
    endGame();
}

export function cleanUpThreeJS() {
    if (typeof cancelAnimationFrame !== 'undefined') {
        cancelAnimationFrame(animationId);
    }

    if (renderer) {
        renderer.dispose();
    }

    if (scene) {
        scene.traverse((object) => {
            if (!object.isMesh) return;
            object.geometry.dispose();

            if (object.material.isMaterial) {
                cleanMaterial(object.material);
            } else {
                for (const material of object.material) cleanMaterial(material);
            }
        });
    }
    if (composer) composer.dispose();
    gameStarted = false;
    const gameContainer = document.getElementById('pongGameContainer');
    if (gameContainer) {
        gameContainer.innerHTML = '';
    }
    if (scene)
        scene = null;
    if (camera)
        camera = null;
    if (composer)
        composer = null;
    if (renderer)
        renderer = null;
}

function cleanMaterial(material) {
    material.dispose();
    for (const key in material) {
        const value = material[key];
        if (value && typeof value === 'object' && 'minFilter' in value) {
            value.dispose();
        }
    }
}

/**
 * startGame
 * Function called to start the game
 * @param {*} containerId container for running the game
 * @param {*} config game properties (id, players, online, tournament)
 * @param {*} onGameEnd callback function that will be called in the end of game
 * @returns if config is invalid, otherwise runs the game
 */
export function startGame(containerId, config = {}, onGameEnd = null) {
    console.log('Config object:', config);  // Debugging line

    const {
        isRemote = false,
        playerIds = [],
        gameId = null,
        isLocalTournament = false
    } = config;
    
    console.log('playerIds:', playerIds);  // Debugging line
    if (playerIds !== null && (!Array.isArray(playerIds) || !playerIds.every(item => item === null || Number.isInteger(item)) || (playerIds.length !== 0 && playerIds.length !== 2))) {
        console.error('Invalid player IDs:', playerIds[0], playerIds[1]);
        return;
    }
    if (gameId !== null && !Number.isInteger(gameId)) {
        console.error('Invalid game ID:', gameId);
        return;
    }
    if (typeof isRemote !== 'boolean' || typeof isLocalTournament !== 'boolean') {
        console.error('Invalid boolean value for isRemote or isLocalTournament:', isRemote, isLocalTournament);
        return;
    }
    if (gameStarted) return;
    let player1Id, player2Id, localPlayerId, finalGameId;
    // if (player1_id === player2_id) {
    //     player2_id++;
    // }
    // gameSession.initialize(game_id, player1_id, player2_id, isRemote, scene);
    if (isLocalTournament === true && isRemote === true) {
        console.error('Local tournaments cannot be remote!');
        return;
    }
    if (isLocalTournament === true) {
        if (gameId === null) {
            console.error('Game ID is missing! Cannot start local tournament game!');
            return;
        }
        if (playerIds.length !== 2) {
            console.error('Player IDs are missing or incomplete! Cannot start local tournament game!');
            return;
        }
        player1Id = playerIds[0]; // Use pre-generated player IDs
        player2Id = playerIds[1];
        finalGameId = gameId;
    }
    else if (isRemote === true) {
        if (gameId === null) {
            console.error('Game ID is missing! Cannot start remote game!');
            return;
        }
        else finalGameId = gameId;
        if (playerIds.length !== 2) {
            console.error('Player IDs are missing or incomplete! Cannot start remote game!');
            return;
        }
        const userData = JSON.parse(localStorage.getItem('userData'));
        console.log('UserData:', userData); // Debugging line
        if (!userData || !userData.id || !userData.token) {
            console.error('UserData is missing or incomplete! Cannot start remote game!');
            return;
        }
        else {
            localPlayerId = userData.id;
        }
        if (localPlayerId === playerIds[0] || localPlayerId === playerIds[1]) {
        player1Id = playerIds[0];
        player2Id = playerIds[1];
        } 
        else {
            console.error('Local player ID does not match player IDs:', localPlayerId, playerIds[0], playerIds[1]);
            return;
        }
    }
    else {
        const userData = JSON.parse(localStorage.getItem('userData'));
        console.log('UserData:', userData); // Debugging line
        if (!userData || !userData.id || !userData.token) {
            console.error('UserData is missing or incomplete!');
        }
        else {
            localPlayerId = userData.id;
        }
        player1Id = Math.round(randFloat(1000, 1999));
        player2Id = Math.round(randFloat(2000, 2999));
        finalGameId = Math.round(randFloat(5000, 9999));
    }
    globalState.invertedView = player2Id === localPlayerId
    const container = document.getElementById(containerId);
    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 600;
    container.appendChild(canvas);

    // Initialize game session

    const { renderer: r, scene: s, camera: c, composer: comp } = init(canvas);
    renderer = r;
    scene = s;
    camera = c;
    composer = comp;
    gameSession = new GameSession();
    gameSession.initialize(finalGameId, localPlayerId, player1Id, player2Id, isRemote, isLocalTournament, scene, onGameEnd);
    gameStarted = true;

    // Keyboard controls
    const keys = {};
    document.addEventListener('keydown', (event) => {
        keys[event.key] = true;
    });
    document.addEventListener('keyup', (event) => {
        keys[event.key] = false;
    });

    function flip() {
        if (keys['f'] || keys['F']) {
            globalState.invertedView = true;
            camera.position.set(400, 400, -400);
            gameSession.scoreBoard.clearScores();
            gameSession.scoreBoard.createScoreBoard("Player 1: 0\nPlayer 2: 0");
        }
        if (keys['r'] || keys['R']) {
            globalState.invertedView = false;
            camera.position.set(-400, 400, 400);
            gameSession.scoreBoard.clearScores();
            gameSession.scoreBoard.createScoreBoard("Player 1: 0\nPlayer 2: 0");
        }
    }

    // Update function
    function localGameControls() {
        let leftDeltaZ = 0;
        let rightDeltaZ = 0;

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
        gameSession.leftPaddle.mesh.position.z += leftDeltaZ;
        gameSession.rightPaddle.mesh.position.z += rightDeltaZ;

        if (leftDeltaZ !== 0 || rightDeltaZ !== 0) {
            let emitData = JSON.stringify({
                'type': 'move_paddle',
                'game_id': gameSession.gameId,
                'player1_id': gameSession.player1Id, 
                'p1_delta_z': leftDeltaZ,
                'player2_id': gameSession.player2Id,
                'p2_delta_z': rightDeltaZ
            });
        gameSession.sendMovement(emitData);
        }
    }
    function remoteGameControls() {
        let deltaZ = 0;
    
        // Capture input for the local player’s paddle
        if (keys['w'] || keys['W']) {
            deltaZ -= PADDLE_SPEED;
        }
        if (keys['s'] || keys['S']) {
            deltaZ += PADDLE_SPEED;
        }
    
        // Update the local player's paddle
        if (localPlayerId === gameSession.player1Id) {
            gameSession.leftPaddle.mesh.position.z += deltaZ;
        } else {
            gameSession.rightPaddle.mesh.position.z -= deltaZ;
        }
    
        // Send movement data to the server for the local player’s paddle
        if (deltaZ !== 0) {
            let emitData = JSON.stringify({
                'type': 'move_paddle',
                'game_id': gameSession.gameId,
                'player_id': localPlayerId,
                'delta_z': deltaZ
            });
            gameSession.sendMovement(emitData);
        }
    }
            // Add remote game controls here
    let controlFunction;
    if (isRemote === true)
        controlFunction = remoteGameControls;
    else
        controlFunction = localGameControls;
    function animate() {
        controlFunction();
        flip();
        updateITimes();
        camera.lookAt(0, 0, 0);
        composer.render();
        animationId = requestAnimationFrame(animate);
    }
    animate();
}



function updateITimes() {
    globalState.iTime += .01;
    if (globalState.playingFieldMaterial)
        globalState.playingFieldMaterial.uniforms.iTime.value = globalState.iTime;
    if (globalState.scoreBoardMaterial)
        globalState.scoreBoardMaterial.uniforms.iTime.value = globalState.iTime;
}
document.addEventListener('DOMContentLoaded', () => {
    const pongModal = new bootstrap.Modal(document.getElementById('pongModal'));

    document.querySelector('button[data-bs-target="#pongModal"]').addEventListener('click', () => {
        setTimeout(() => {
            startGame('pongGameContainer', {
                isRemote: false,  // Set to true for remote multiplayer
                playerIds: [],    // Specify player IDs if needed
                gameId: null,     // Specify game ID if needed
                isLocalTournament: false,  // Set to true for local tournaments
            }, callBackTestFunction);
        }, 500); // Ensure the modal is fully visible
    });

    document.getElementById('pongModal').addEventListener('hidden.bs.modal', () => {
        if (gameStarted) {
            endGame();
        }
    });    
});

export function cleanUpGame() {
    if (gameSession)
    {
        gameSession.disconnect();
        gameSession = null;
    }
}
export function endGame()
{
    cleanUpThreeJS();
    cleanUpGame();
    gameStarted = false;
    localStorage.setItem('isGameOver', 'true');
    console.log("at endgame: gameStarted:", gameStarted, "isGameOver:", localStorage.getItem('isGameOver'));
}

export function changeCameraAngle()
{
    camera.position.set(0, 400, 400);
    camera.lookAt(0, 0, 0)
}

