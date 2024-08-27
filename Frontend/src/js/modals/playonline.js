import * as bootstrap from 'bootstrap';
import { startGame } from '../pong/pong';
import { handleTokenVerification } from '../tokenHandler';
import { showMessage } from './messages';
const pongModalElement = document.getElementById('pongModal');
const waitingLobbyModalElement = document.getElementById('waitingLobbyModal');
const waitingLobbyModalLabel = document.getElementById('waitingLobbyModalLabel');
const lobbyContent = document.getElementById('lobbyContent');

// Initialize modals
const pongModal = new bootstrap.Modal(pongModalElement);
const waitingLobbyModal = new bootstrap.Modal(waitingLobbyModalElement);

// Function to open the waiting lobby
export function openWaitingLobby() {
    waitingLobbyModal.show();
    const cancelButton = document.getElementById('cancelOnlinePlay');
    
    // Check if the button exists before trying to update it
    if (cancelButton) {
        // Update the button's text
        cancelButton.textContent = 'Cancel';
    }
    lobbyContent.innerHTML = 
    `<div class="d-flex justify-content-center">
        <div class="spinner-border" style="width: 4rem; height: 4rem;" role="status">
            <span class="visually-hidden">Waiting for players...</span>
        </div>
    </div>`;
    waitingLobbyModalLabel.textContent = "Waiting for players..";

    setTimeout(() => {
        connectToWebSockets();
    }, 1000);
}

function connectToWebSockets() {
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData || !userData.token) {
         console.error('User data or token is missing');
         return;
    }
    handleTokenVerification()
    .then(validToken => {
        userData.token = validToken;
        const onlineStatusSocket = new WebSocket(`/ws/online/?token=${validToken}`);    

    let gameRoomSocket;

    onlineStatusSocket.onopen = function() {
    };

    onlineStatusSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'wait_for_opponent') {
            const roomName = data.room_name;
            connectToGameRoom(roomName);
        } else if (data.type === 'match_found') {
            const roomName = data.room_name;
            connectToGameRoom(roomName);
            lobbyContent.innerHTML = 
            `<div class="d-flex justify-content-center">
                <div class="spinner-border" style="width: 4rem; height: 4rem;" role="status">
                    <span class="visually-hidden">Match found! Connecting..</span>
                </div>
            </div>`;
            waitingLobbyModalLabel.textContent = "Match found! Connecting..";
        }
    };

    onlineStatusSocket.onclose = function(event) {
    };

    onlineStatusSocket.onerror = function(error) {
        showMessage("An error occured while connecting to matchmaking", waitingLobbyModal, error)
        setTimeout(() => {
            waitingLobbyModal.hide();
        }, 2500);
    };

    function connectToGameRoom(roomName) {
        handleTokenVerification()
        .then(validToken => {
            userData.token = validToken;
            gameRoomSocket = new WebSocket(`/ws/game/room/${roomName}/?token=${validToken}`);

                gameRoomSocket.onopen = function() {
                    gameRoomSocket.send(JSON.stringify({ type: 'join', username: userData.username }));
                };

                gameRoomSocket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'starting_game') {
                        waitingLobbyModalLabel.textContent = "Starting game..";

                        let config = {
                            isRemote: true,
                            gameId: data.message.game_id,
                            playerIds: [data.message.player1_id, data.message.player2_id],
                            player1Alias: data.message.player1_username,
                            player2Alias: data.message.player2_username,
                            isLocalTournament: false,
                        };

                        if (onlineStatusSocket.readyState === WebSocket.OPEN) {
                            onlineStatusSocket.close();
                        }

                        if (gameRoomSocket && gameRoomSocket.readyState === WebSocket.OPEN) {
                            gameRoomSocket.close();
                        }

                        waitingLobbyModal.hide();
                        startGame('pongGameContainer', config, handleGameEnd);
                    }
                };

                gameRoomSocket.onclose = function(event) {
                    
                };

                gameRoomSocket.onerror = function(error) {
                    showMessage("An error occured while connecting to matchmaking", waitingLobbyModal, error)
                    setTimeout(() => {
                        waitingLobbyModal.hide();
                    }, 2500);
                };
            }
        )}
    waitingLobbyModalElement.addEventListener('hide.bs.modal', function () {
        if (onlineStatusSocket.readyState === WebSocket.OPEN) {
            onlineStatusSocket.close();
        }

        if (gameRoomSocket && gameRoomSocket.readyState === WebSocket.OPEN) {
            gameRoomSocket.close();
        }
    });
})
.catch(error => {
    showMessage("Error verifying token", waitingLobbyModal, error)
    setTimeout(() => {
        waitingLobbyModal.hide();
    }, 2500);});

}

function handleGameEnd(data) {
    
    waitingLobbyModal.show();
    const cancelButton = document.getElementById('cancelOnlinePlay');
    
    // Check if the button exists before trying to update it
    if (cancelButton) {
        // Update the button's text
        cancelButton.textContent = 'Close';
    }
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData || !userData.token) {
        console.error('User data or token is missing');
        return;
    }
    waitingLobbyModalLabel.textContent = "Game over";
    fetch(`/game-history/${data.game_id}/`)
        .then(response => response.json())
        .then(gameHistoryRecord => {
            lobbyContent.innerHTML = `<p class="font">Final Score:</p>
            <p class="font">${gameHistoryRecord.player1_username}: ${data.player1_score}</p>
            <p class="font">${gameHistoryRecord.player2_username}: ${data.player2_score}</p>
            <p class="font">Total hits:</p>
            <p class="font">${gameHistoryRecord.player1_username}: ${data.player1_hits}</p>
            <p class="font">${gameHistoryRecord.player2_username}: ${data.player2_hits}</p>
            <p class="font">Longest rally: ${data.longest_rally * 0.016}</p>`;
            if (Number(userData.id) === data.winner){
                updateGameHistory(data, gameHistoryRecord);
            }
        });
    }

function updateGameHistory(data, gameHistoryRecord) {
    fetch(`/game-history/${data.game_id}/`)
        .then(response => response.json())
        .then(gameHistoryRecord => {
            if (gameHistoryRecord.winner_id === data.winner) {
                console.log(gameHistoryRecord);
                return;
            } else {
                gameHistoryRecord.winner_id = data.winner;
                return fetch(`/game-history/${data.game_id}/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(gameHistoryRecord)
                });
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const gameStatData = {
                game_id: data.game_id,
                player1_score: data.player1_score,
                player2_score: data.player2_score,
                player1_hits: data.player1_hits,
                player2_hits: data.player2_hits,
                longest_rally: data.longest_rally
            };
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
        .catch(error => {
            console.error('Error:', error);
        });
}
