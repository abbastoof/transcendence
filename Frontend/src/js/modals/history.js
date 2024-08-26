import { showMessage } from "./messages";

document.addEventListener('DOMContentLoaded', function () {
    updateMatchHistory();
});

export function updateMatchHistory() {
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData || !userData.id || !userData.token) {
        return;
    }

    const userId = Number(userData.id); // Ensure user ID is a number

    fetch(`/game-history/`, {
        method: 'GET',
        headers: {
            // Include authorization headers if needed
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(error => {
                throw new Error(error.detail || 'Network response was not ok');
            });
        }
        return response.json();
    })
    .then(data => {
        const gameHistoryContainer = document.getElementById('History');
        if (!gameHistoryContainer) {
            return;
        }

        // Calculate wins and losses
        let wins = 0;
        let losses = 0;

        data.forEach(game => {
            if (game.winner_id === userId) {
                wins++;
            } else if ((game.player1_id === userId || game.player2_id === userId) && game.winner_id !== userId) {
                losses++;
            }
        });

        // Build HTML content for wins and losses
        let statsHtml = `
            <div class="font" style="margin-top: -20px">
                <span>Wins:</span> &nbsp; ${wins} &nbsp;&nbsp; <span>Losses:</span> &nbsp; ${losses}
            </div>
            <div class="container">
                <h2 class="font">Game History</h2>
        `;

        // Build HTML content for game records
        let gameHistoryHtml = '';
        let gameCounter = 1;
        data.forEach(game => {
            if (game.player1_id === userId || game.player2_id === userId) {
                let winner_name;
                if (game.winner_id === game.player1_id) {
                    winner_name = game.player1_username;
                } else if (game.winner_id === game.player2_id) {
                    winner_name = game.player2_username;
                }

                gameHistoryHtml += `
                    <div class="game-record">
                        <h3 class="game-font">Game ${gameCounter}</h3>
                        <p class="game-label">${new Date(game.start_time).toLocaleString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                        <p class="game-label">${game.player1_username} - ${game.player2_username}</p>
                        <p class="game-label">Winner: <i><u><b>${winner_name}</b></i></u></p>
                    </div>
                `;
                gameCounter++;
            }
        });

        // Combine stats and game history HTML
        let htmlContent = statsHtml + gameHistoryHtml + '</div>';

        // Set the HTML content to the container
        gameHistoryContainer.innerHTML = htmlContent;
    })
    .catch(error => {
        showMessage('Error fetching game history: ' + error.message, '#gameHistoryModal', 'error');
        const gameHistoryContainer = document.getElementById('History');
        if (gameHistoryContainer) {
            gameHistoryContainer.innerHTML = `<p>Error fetching game history: ${error.message}</p>`;
        }
    });
};
