// pong.js
import * as bootstrap from 'bootstrap';
import * as THREE from 'three'
import GameSession from './classes/GameSession.js';
import { init } from './init.js';
import { randFloat } from 'three/src/math/MathUtils.js';
import { globalState } from './globalState.js';
import { localGameControls, remoteGameControls } from './controls.js';
import { cleanupEventHandlers } from './eventhandlers.js';

let gameStarted = false;
let gameSession, renderer, scene, camera, composer, animationId;

/**
 * validateConfig
 * Function to validate the configuration object
 * @param {*} config is the configuration object
 * @returns returns true if the configuration is valid, otherwise false
 */
function validateConfig(config) {

    const {
        isRemote = false,
        gameId = null,
        playerIds = [],
        player1Alias = "Player1",
        player2Alias = "Player2",
        isLocalTournament = false,
        isTest = false,
    } = config;
    
    console.log('playerIds:', playerIds);  // Debugging line
    if (playerIds !== null && (!Array.isArray(playerIds) || !playerIds.every(item => item === null || Number.isInteger(item)) || (playerIds.length !== 0 && playerIds.length !== 2))) {
        console.error('Invalid player IDs:', playerIds[0], playerIds[1]);
        return false;
    }
    if (gameId !== null && !Number.isInteger(gameId)) {
        console.error('Invalid game ID:', gameId);
        return false;
    }
    if (typeof isRemote !== 'boolean' || typeof isLocalTournament !== 'boolean') {
        console.error('Invalid boolean value for isRemote or isLocalTournament:', isRemote, isLocalTournament);
        return false;
    } 
    if (isLocalTournament === true && isRemote === true) {
        console.error('Local tournaments cannot be remote!');
        return false;
    }
    if (isRemote === true && (playerIds.length !== 2 || gameId === null)) {
        console.error('Remote games require player IDs and game ID!');
        return false;
    }
    return true
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

    if (!validateConfig(config)) return;
    if (gameStarted) return;
    let player1Id, player2Id, finalGameId, localPlayerId;

    if (isLocalTournament === true) {
        player1Id = playerIds[0]; // Use pre-generated player IDs
        player2Id = playerIds[1];
        finalGameId = gameId;
    }
    else if (isRemote === true) {
        finalGameId = gameId;
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        console.log('UserData:', userData); // Debugging line
        if (!userData || !userData.id || !userData.token) {
            console.error('UserData is missing or incomplete! Cannot start remote game!');
            endGame();
            return;
        }
        else {
            localPlayerId = Number(userData.id);
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
        const userData = JSON.parse(sessionStorage.getItem('userData'));
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

    const { renderer: r, scene: s, camera: c, composer: comp } = init(canvas);
    renderer = r;
    scene = s;
    camera = c;
    composer = comp;
    gameSession = new GameSession();
    gameSession.initialize(finalGameId, localPlayerId, player1Id, player2Id, player1Alias, player2Alias, isRemote, isLocalTournament, scene, onGameEnd);
    gameStarted = true;

    // This section defines which function is used for player controls
    // If the game is remote, the remoteGameControls function is used
    // Otherwise, the localGameControls function is used
    let controlFunction;
    if (isRemote === true)
        controlFunction = remoteGameControls;
    else
        controlFunction = localGameControls;

    // Animation loop
    // This function is called recursively to animate the game
    // It calls the controlFunction which listens to player controls
    // It updates the iTime variable for the shaders
    // Points the camera to center of the scene
    // It renders the scene using the composer
    // It requests the next animation frame

    function animate() {
        controlFunction(gameSession);
        updateITimes();

        camera.lookAt(0, 0, 0);
        composer.render();
        animationId = requestAnimationFrame(animate);
    }
    animate();
}

function quitRemoteGame() {
    if (gameSession) {
        gameSession.quitGame();
    }

}

// Function to update the iTime variable for the shaders
// This function is called in the animate function
// It increments the iTime variable by .01 and updates iTime for all animated shaders
function updateITimes() {
    globalState.iTime += .01;
    if (globalState.playingFieldMaterial)
        globalState.playingFieldMaterial.uniforms.iTime.value = globalState.iTime;
    if (globalState.scanlinePass)
        globalState.scanlinePass.uniforms.iTime.value = globalState.iTime;
    if (gameSession.scoreBoard.materials) {
        gameSession.scoreBoard.materials.forEach(material => {
            material.uniforms.iTime.value = globalState.iTime;
        });
    }
}

// Event listener for the Pong modal
// This event listener is added to the button for starting the local game
// opens themodal and starts the game
document.addEventListener('DOMContentLoaded', () => {
    const pongModal = new bootstrap.Modal(document.getElementById('pongModal'));

    document.querySelector('button[data-bs-target="#pongModal"]').addEventListener('click', () => {
        setTimeout(() => {
            startGame('pongGameContainer', {
                isRemote: false,  // Set to true for remote multiplayer
                playerIds: [],    // Specify player IDs if needed
                gameId: null,     // Specify game ID if needed
                isLocalTournament: false,  // Set to true for local tournaments
            }, localGameCallBack);
        }, 500); // Ensure the modal is fully visible
    });

    document.getElementById('pongModal').addEventListener('hidden.bs.modal', () => {
        if (gameStarted) {
            if (gameSession.isRemote === true && gameSession.inProgress === true) {
                quitRemoteGame();
            }
            else
                endGame();
        }
    });    
});

/**
 * Function to clean up the game
 * Removes all game resources and resets the game state
 * @returns void
 * @modifies gameSession, scene, camera, composer, renderer
 * @effects clears the game container
 * @effects removes the animation frame
 * @effects disposes the renderer
 * @effects disposes the composer
 * @effects nulls the game session
 */
export function cleanUpGame() {
    if (gameSession) gameSession = null;
    console.log(gameSession)
    if (scene) scene = null;
    if (camera) camera = null;
    if (composer) composer = null;
    if (renderer) renderer = null;
    if (composer) composer.dispose();
    const gameContainer = document.getElementById('pongGameContainer');
    if (gameContainer) {
        gameContainer.innerHTML = '';
    }
}

function localGameCallBack(data) {
    const gameContainer = document.getElementById('pongGameContainer');
    if (gameContainer) {
        gameContainer.innerHTML = ''
        ;
    }
}

/**
 * Function to end the game
 * Cleans up the game and sets the game state to ended
 * @returns void
**/
export function endGame() {    
    console.log("Starting endGame cleanup...");

    if (typeof cancelAnimationFrame !== 'undefined') {
        cancelAnimationFrame(animationId);
        console.log("Animation frame cancelled.");
    }

    if (renderer) {
        renderer.dispose();
        console.log("Renderer disposed.");
    }

    if (gameSession) {
        gameSession.clearResources();
        console.log("Game session resources cleared.");
    }

    cleanUpGame();

    gameStarted = false;
    sessionStorage.setItem('isGameOver', 'true');

    console.log("EndGame complete, gameStarted:", gameStarted, "isGameOver:", sessionStorage.getItem('isGameOver'));


    console.log("Modal hide attempted at endGame.");
}
