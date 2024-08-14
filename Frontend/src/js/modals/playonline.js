import * as bootstrap from 'bootstrap';
import { startGame } from '../pong/pong';

const pongModal = new bootstrap.Modal(document.getElementById('pongModal')); // Peli modalin määrittely
var waitingLobbyModalLabel = document.getElementById('waitingLobbyModalLabel');
var lobbyContent = document.getElementById('lobbyContent')

// Function to open the waiting lobby
export function openWaitingLobby() {
    var waitingLobbyModal = new bootstrap.Modal(document.getElementById('waitingLobbyModal'));
    waitingLobbyModal.show();

    lobbyContent.innerHTML = 
    `<div class="d-flex justify-content-center">
        <div class="spinner-border"  style="width: 4rem; height: 4rem;" role="status">
            <span class="visually-hidden">Waiting for players...</span>
        </div>
    </div>
    `
    waitingLobbyModalLabel.textContent = "Waiting for players.."

    //document.getElementById('startGameButton').addEventListener('click', startRemoteGame);
    // Simulate a call to the server to find other players
    setTimeout(() => {
        connectToWebSockets();
    }, 1000);

//    searchForPlayers();
}

function connectToWebSockets() {

    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData || !userData.token) {
        console.error('User data or token is missing');
        return;
    }

    // Connect to the online status WebSocket
    const onlineStatusSocket = new WebSocket(`/ws/online/?token=${userData.token}`);

    let gameRoomSocket;

    // Setup WebSocket event handlers for online status
    onlineStatusSocket.onopen = function() {

        console.log('Connected to online status WebSocket');
    };

    onlineStatusSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'wait_for_opponent') {
            // Room has been assigned, connect to the game room WebSocket
            const roomName = data.room_name;
            connectToGameRoom(roomName);
        }
        else if (data.type === 'match_found')
        {
            const roomName = data.room_name;
            connectToGameRoom(roomName);   
            lobbyContent.innerHTML = 
            `<div class="d-flex justify-content-center">
                <div class="spinner-border"  style="width: 4rem; height: 4rem;" role="status">
                    <span class="visually-hidden">Match found! Connecting..</span>
                </div>
            </div>
            `
            waitingLobbyModalLabel.textContent = "Match found! Connecting.."
        }
    };

    onlineStatusSocket.onclose = function(event) {
        console.log('Online status WebSocket closed:', event);
    };

    onlineStatusSocket.onerror = function(error) {
        console.error('Error in online status WebSocket:', error);
    };

    // Function to connect to the game room WebSocket
    function connectToGameRoom(roomName) {
        gameRoomSocket = new WebSocket(`/ws/game/room/${roomName}/?token=${userData.token}`);

        gameRoomSocket.onopen = function() {
            console.log(`Connected to game room ${roomName} WebSocket`);
            // Notify server that the user has joined the room
            gameRoomSocket.send(JSON.stringify({ type: 'join', username: userData.username }));
        };

        gameRoomSocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('Received from game room WebSocket:', data);
            if (data.type === 'starting_game') {
                lobbyContent.innerHTML = 
                    `<div class="d-flex justify-content-center">
                        <div class="spinner-border"  style="width: 4rem; height: 4rem;" role="status">
                            <span class="visually-hidden">Match found! Connecting..</span>
                        </div>
                    </div>
                    `
                
                waitingLobbyModalLabel.textContent = "Starting game.."
                
                let config = {
                    isRemote: true,
                    gameId: data.message.game_id,
                    playerIds: [ data.message.player1_id, data.message.player2_id ],
                    player1Alias: data.message.player1_username,
                    player2Alias: data.message.player2_username,
                    isLocalTournament: false,
                }
                            // Close the waiting lobby modal

                // Close the online status WebSocket
                if (onlineStatusSocket.readyState === WebSocket.OPEN) {
                    onlineStatusSocket.close();
                }

                // Close the game room WebSocket if it exists and is open
                if (gameRoomSocket && gameRoomSocket.readyState === WebSocket.OPEN) {
                    gameRoomSocket.close();
                }
                pongModal.show();
                startGame('pongGameContainer', config, handleGameEnd);
            }
        };

        gameRoomSocket.onclose = function(event) {
            console.log(`Game room ${roomName} WebSocket closed:`, event);
        };

        gameRoomSocket.onerror = function(error) {
            console.error(`Error in game room ${roomName} WebSocket:`, error);
        };
    }
    var waitingLobbyModal = document.getElementById('waitingLobbyModal');
    waitingLobbyModal.addEventListener('hide.bs.modal', function () {
        console.log('Modal is closing. Disconnecting WebSockets.');

        // Close the online status WebSocket
        if (onlineStatusSocket.readyState === WebSocket.OPEN) {
            onlineStatusSocket.close();
        }

        // Close the game room WebSocket if it exists and is open
        if (gameRoomSocket && gameRoomSocket.readyState === WebSocket.OPEN) {
            gameRoomSocket.close();
        }
    });
}

function handleGameEnd(data) {
    // Update the game history record with the winner_id
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData || !userData.token) {
        console.error('User data or token is missing');
        return;
    }
    if (Number(userData.id) !== data.winner){
        waitingLobbyModalLabel.textContent = "Game over";
        lobbyContent.innerHTML = `<p>you are a loser. so sad.</p>`
        return;
    }
    console.log('Updating game history record with winner_id:', data.winner);
    waitingLobbyModalLabel.textContent = "Game over";
    lobbyContent.innerHTML = `<p>you are a winner</p>`
    
    fetch(`/game-history/${data.game_id}/`)
        .then(response => response.json())
        .then(gameHistoryRecord => {
            // Update the winner_id field
            if (gameHistoryRecord === data.winner) {
                console.log(gameHistoryRecord)
                return;
            }
            else 
                gameHistoryRecord.winner_id = data.winner;
            return fetch(`/game-history/${data.game_id}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(gameHistoryRecord)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Create the game statistics record
            const gameStatData = {
                game_id: data.game_id,
                player1_score: data.player1_score,
                player2_score: data.player2_score,
                total_hits: data.player1_hits + data.player2_hits,
                longest_rally: data.longest_rally
            };
            console.log('Creating game stat record:', gameStatData);
            return fetch('/game-stat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(gameStatData)
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Game stat record created:', data);
        })
        .catch(error => {
            console.error('Error:', error);
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

