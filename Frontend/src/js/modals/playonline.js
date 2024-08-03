import * as bootstrap from 'bootstrap';
import { startGame } from '../pong/pong';

// Function to open the waiting lobby
export function openWaitingLobby() {
    var waitingLobbyModal = new bootstrap.Modal(document.getElementById('waitingLobbyModal'));
    waitingLobbyModal.show();

    document.getElementById('startGameButton').addEventListener('click', startRemoteGame);
    // Simulate a call to the server to find other players
    searchForPlayers();
}

// Function to search for other players
function searchForPlayers() {
    var lobbyMessage = document.getElementById('lobbyMessage');

    // Example of searching for players (replace with actual server call)
    fetch('/game/search-players/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.playersFound) {
            lobbyMessage.textContent = 'Players found! Starting game...';
            // Implement logic to start the game
        } else {
            lobbyMessage.textContent = 'Waiting for players...';
            // Continue polling or use websockets for real-time updates
            setTimeout(searchForPlayers, 5000); // Retry after 5 seconds
        }
    })
    .catch(error => {
        console.error('Error searching for players:', error);
        lobbyMessage.textContent = 'Error searching for players. Please try again later.';
    });
}


// Function to start the remote game
export function startRemoteGame(gameId, playerIds) {
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
        isRemote: true,
        isLocalTournament: false
    };

    console.log('Starting remote game with config:', config);

    // Start the game with the provided configuration
    startGame('pongGameContainer', config);

    // Show the Pong modal
    window.pongModal.show();
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('startGameButton').addEventListener('click', function () {
        const gameId = document.getElementById('gameId').value.trim();
        const playerId1 = document.getElementById('playerId1').value.trim();
        const playerId2 = document.getElementById('playerId2').value.trim();

        if (!gameId || !playerId1 || !playerId2) {
            console.error('Please provide a game ID and both player IDs.');
            return;
        }

        // Call the function from playonline.js
        import('./playonline.js').then(module => {
            module.startRemoteGame(gameId, [playerId1, playerId2]);
        });
    });
});