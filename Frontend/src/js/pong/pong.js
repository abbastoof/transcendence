// pong.js
import * as bootstrap from 'bootstrap';
import * as THREE from 'three'
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
        gameId = null,
        playerIds = [],
        player1Alias = "Player1",
        player2Alias = "Player2",
    //  localPlayerId = null,
        isLocalTournament = false,
        isTest = false,
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
    let player1Id, player2Id, finalGameId, localPlayerId;
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
            endGame();
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
        // const userData = JSON.parse(localStorage.getItem('userData'));
        // console.log('UserData:', userData); // Debugging line
        // if (!userData || !userData.id || !userData.token) {
        //     console.error('UserData is missing or incomplete!');
        // }
        // else {
        //     localPlayerId = userData.id;
        // }
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
    gameSession.initialize(finalGameId, localPlayerId, player1Id, player2Id, player1Alias, player2Alias, isRemote, isLocalTournament, scene, onGameEnd);
    gameStarted = true;

    // Keyboard controls
    const keys = {};
    document.addEventListener('keydown', (event) => {
        keys[event.key] = true;
    });
    document.addEventListener('keyup', (event) => {
        keys[event.key] = false;
    });

    let keyPressed = false; // Flag to track if the key is currently pressed

    function changeView() {
        if (keys['c'] || keys['C']) {
            if (!keyPressed) { // Check if the key was not already pressed
                keyPressed = true; // Set the flag to indicate the key is now pressed
    
                if (globalState.view2D === false) {
                    globalState.view2D = true;
                    if (globalState.invertedView === true) {
                        camera.position.set(0, 400, -400);
                    } else {
                        camera.position.set(0, 400, 400);
                    }
                } 
                else {
                    if (globalState.invertedView === true) {
                        camera.position.set(400, 400, -400); // Adjust these values for your desired isometric angle
                    }
                    else {
                        camera.position.set(-400, 400, 400);
                        globalState.view2D = false;
                    }
                    gameSession.scoreBoard.clearScores();
                    gameSession.scoreBoard.updateScores(gameSession.player1Alias, gameSession.player1Score, gameSession.player2Alias, gameSession.player2Score);
                }
            }
            else {
            keyPressed = false; // Reset the flag when the key is released
            }
        }
    }

    // Update function
    function localGameControls() {
        let leftDeltaZ = 0;
        let rightDeltaZ = 0;
        if (gameSession.paused === true) {
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
    function remoteGameControls() {
        let deltaZ = 0;
        
        if (gameSession.paused === true) {
            return;
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
    
        // Send movement data to the server for the local player’s paddle
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
            // Add remote game controls here
    let controlFunction;
    if (isRemote === true)
        controlFunction = remoteGameControls;
    else
        controlFunction = localGameControls;
    function animate() {
        controlFunction();
        changeView();
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
    if (gameSession.scoreBoard.materials) {
        gameSession.scoreBoard.materials.forEach(material => {
            material.uniforms.iTime.value = globalState.iTime;
        });
    }
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

