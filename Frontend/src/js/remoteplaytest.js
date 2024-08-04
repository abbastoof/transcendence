import '../scss/styles.scss'
import * as bootstrap from 'bootstrap'
import {startGame, cleanUpGame} from './pong/pong.js'

// Assuming you have imported necessary modules and functions like startGame, cleanupGame
document.addEventListener('DOMContentLoaded', function () {
    // Initialize the modal with options to prevent closing on backdrop click
    const pongModalElement = document.getElementById('pongModal');
    const pongModal = new bootstrap.Modal(pongModalElement, {
        backdrop: 'static',
        keyboard: true // Optional: prevents closing with ESC key
    });

    // Show the modal and start the game when it's opened
    pongModalElement.addEventListener('shown.bs.modal', function () {
        
    });

    // Clean up game resources when the modal is closed
    pongModalElement.addEventListener('hidden.bs.modal', function () {
        cleanUpGame();
    });
    // Make modal available globally if needed
    window.pongModal = pongModal;
    // Optionally, add event listeners for other modals if needed
});

// Function to start the remote game
export function startRemoteGame(gameId, playerIds, localPlayerId) {
    const pongModalElement = document.getElementById('pongModal');
    
    // Check if pongModal is initialized
    if (!window.pongModal) {
        console.error('Pong modal is not initialized.');
        return;
    }
    
    // Validate input
    if (!gameId || !playerIds || playerIds.length !== 2) {
        console.error('Invalid game ID or player IDs.');
        return;
    }

    const config = {
        gameId: parseInt(gameId, 10),
        playerIds: playerIds.map(id => parseInt(id, 10)),
        localPlayerId: parseInt(localPlayerId, 10),
        isRemote: true,
        isLocalTournament: false,
        isTest: true
    };

    console.log('Starting remote game with config:', config);

    // Start the game with the provided configuration
    startGame('pongGameContainer', config, true);

    // Show the Pong modal
    pongModal.show();
}


document.addEventListener('DOMContentLoaded', () => {
    const onlineTestModal = new bootstrap.Modal(document.getElementById('onlineTestModal'));
    onlineTestModal.show()});

    document.addEventListener('DOMContentLoaded', function () {
        document.getElementById('startRemoteGameButton').addEventListener('click', function () {
            const gameId = document.getElementById('gameId').value.trim();
            const playerId1 = document.getElementById('playerId1').value.trim();
            const playerId2 = document.getElementById('playerId2').value.trim();
            const localPlayerId = document.getElementById('localPlayerId').value.trim();
    
            if (!gameId || !playerId1 || !playerId2 || !localPlayerId) {
                console.error('Please provide a game ID and both player IDs.');
                return;
            }
    
                startRemoteGame(gameId, [playerId1, playerId2], localPlayerId);
            });
        });
