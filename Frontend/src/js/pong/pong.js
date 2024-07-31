// pong.js
import * as bootstrap from 'bootstrap';
import GameSession from './classes/GameSession.js';

import { PADDLE_SPEED } from './constants.js';
import { init } from './init.js';
import { randomMultiplier, randomX, randomY } from './constants.js';
let gameSession = new GameSession();
let gameStarted = false;
let renderer, scene, camera, composer, animationId;

export function cleanupGame() {
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

    const gameContainer = document.getElementById('pongGameContainer');
    if (gameContainer) {
        gameContainer.innerHTML = '';
    }
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

export function startGame(containerId, config = {}) {
    console.log('Config object:', config);  // Debugging line

    const {
        isRemote = false,
        playerIDs = [],
        gameID = null,
        isLocalTournament = false
    } = config;
    if (gameStarted) return;
    gameStarted = true;
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
    let game_id, player1_id, player2_id;
    // if (player1_id === player2_id) {
    //     player2_id++;
    // }
    // gameSession.initialize(game_id, player1_id, player2_id, isRemote, scene);
    if (isLocalTournament === true && isRemote === false) {
        game_id = gameID; // Use pre-generated game ID for tournaments
        player1_id = playerIDs[0]; // Use pre-generated player IDs
        player2_id = playerIDs[1];
    } else if (isRemote === true && isLocalTournament === false) {
        game_id = gameID; // Use provided game ID for remote games
        player1_id = playerIDs[0];
        player2_id = playerIDs[1];
    } else {
        // Generate player IDs for local games
        player1_id = Math.round(randomMultiplier);
        player2_id = Math.round(randomX);
        if (player1_id === player2_id) player2_id++;
        game_id = Math.round(randomY);
    }
    gameSession.initialize(game_id, player1_id, player2_id, isRemote, isLocalTournament, scene);

    // Keyboard controls
    const keys = {};
    document.addEventListener('keydown', (event) => {
        keys[event.key] = true;
    });
    document.addEventListener('keyup', (event) => {
        keys[event.key] = false;
    });

    // Update function
    function updatePaddlePosition() {
        let leftDeltaZ = 0;
        let rightDeltaZ = 0;
    
        if ((keys['q'] || keys['Q']) && !gameSession.leftPaddle.intersectsWall(gameSession.playingField.upperWall.boundingBox)) {
            leftDeltaZ -= PADDLE_SPEED;
        }
        if ((keys['a'] || keys['A']) && !gameSession.leftPaddle.intersectsWall(gameSession.playingField.lowerWall.boundingBox)) {
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

    function animate() {
        updatePaddlePosition();
        gameSession.playingField.shaderMaterial.uniforms.iTime.value = performance.now() / 1000;
        camera.lookAt(0, 0, 0);
        composer.render();
        animationId = requestAnimationFrame(animate);
    }
    animate();
}

function cleanUpThreeJS() {
    if (animationId) cancelAnimationFrame(animationId);
    if (renderer) renderer.dispose();
    if (composer) composer.dispose();
    gameStarted = false;
}

document.addEventListener('DOMContentLoaded', () => {
    const pongModal = new bootstrap.Modal(document.getElementById('pongModal'));

    document.querySelector('button[data-bs-target="#pongModal"]').addEventListener('click', () => {
        setTimeout(() => {
            startGame('pongGameContainer', {
                isRemote: false,  // Set to true for remote multiplayer
                playerIDs: [1234, 5192],    // Specify player IDs if needed
                gameID: null,     // Specify game ID if needed
                isLocalTournament: false  // Set to true for local tournaments
            }); // Set to true for remote multiplayer
        }, 500); // Ensure the modal is fully visible
    });

    document.getElementById('pongModal').addEventListener('hidden.bs.modal', () => {
        cleanUpThreeJS();
        gameSession.disconnect();  // Handle socket disconnection
    });
});
