// pong.js
import * as bootstrap from 'bootstrap';
import * as THREE from 'three'
import GameSession from './classes/GameSession.js';
import { init } from './init.js';
import { randFloat } from 'three/src/math/MathUtils.js';
import { globalState } from './globalState.js';
import { localGameControls, remoteGameControls } from './controls.js';

let gameStarted = false;
let gameSession, renderer, scene, camera, composer, animationId;

function callBackTestFunction(data) {
    console.log(data);
    console.log("callback called back");
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

function validateConfig(config) {

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

    // Update function
    let controlFunction;
    if (isRemote === true)
        controlFunction = remoteGameControls;
    else
        controlFunction = localGameControls;
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
        endGame();
    }

}

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
            if (isRemote === true) {
                quitRemoteGame();
            }
            else
                endGame();
        }
    });    
});

export function cleanUpGame() {
    gameSession = null;
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

export function endGame()
{    
    if (typeof cancelAnimationFrame !== 'undefined') cancelAnimationFrame(animationId);
    if (renderer) renderer.dispose();
    gameSession.clearResources();
    cleanUpGame();
    gameStarted = false;
    sessionStorage.setItem('isGameOver', 'true');
    console.log("at endgame: gameStarted:", gameStarted, "isGameOver:", sessionStorage.getItem('isGameOver'));
}
