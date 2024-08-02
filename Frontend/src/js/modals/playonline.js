import * as bootstrap from 'bootstrap';

// Function to open the waiting lobby
export function openWaitingLobby() {
    var waitingLobbyModal = new bootstrap.Modal(document.getElementById('waitingLobbyModal'));
    waitingLobbyModal.show();

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
