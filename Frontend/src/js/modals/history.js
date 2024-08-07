document.addEventListener('DOMContentLoaded', function () {
    updateMatchHistory();
});

export function updateMatchHistory() {
    const userData = JSON.parse(localStorage.getItem('userData'));
    if (!userData || !userData.id || !userData.token) {
        console.error('UserData is missing or incomplete');
        return;
    }
    fetch(`/game-history/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${userData.token}`
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
            console.error('GameHistory container not found');
            return;
        }
        let htmlContent = '<div class="container mt-4"><h2>Game History</h2>';
        data.forEach(game => {
            if (game.player1_id === userData.id || game.player2_id === userData.id) {
                htmlContent += `
                <div class="game-record mb-3">
                    <h3>Game: ${game.game_id}</h3>
                    <p>Date Played: ${game.start_time}</p>
                    <p>Outcome: ${game.player1_id} - ${game.player2_id}</p>
                `;
                // Get the game details
                fetch(`/game-history/${game.game_id}/`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${userData.token}`
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
                .then(stats => {
                    htmlContent += `
                    <p>${stats.player1_score} - ${stats.player2_score}</p>
                    </div>
                    `;
                    gameHistoryContainer.innerHTML = htmlContent;
                })
                .catch(error => {
                    console.error(`Error fetching game details for game ${game.game_id}:`, error.message);
                    htmlContent += `<p>Error fetching game details: ${error.message}</p></div>`;
                    gameHistoryContainer.innerHTML = htmlContent;
                });
            }
        });
        htmlContent += '</div>';
        gameHistoryContainer.innerHTML = htmlContent;
    })
    .catch(error => {
        console.error('Error fetching game history:', error.message);
        const gameHistoryContainer = document.getElementById('History');
        if (gameHistoryContainer) {
            gameHistoryContainer.innerHTML = `<p>Error fetching game history: ${error.message}</p>`;
        }
    });
};