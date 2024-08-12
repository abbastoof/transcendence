document.addEventListener('DOMContentLoaded', function () {
    const checkUserData = setInterval(() => {
        const userData = sessionStorage.getItem('userData');
        if (userData) {
            clearInterval(checkUserData);
            updateMatchHistory();
        }
    }, 200); // Check every 200ms
});

export function updateMatchHistory() {
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData || !userData.id || !userData.token) {
        console.error('UserData is missing or incomplete');
        return;
    }
    fetch(`/game-history/`, {
        method: 'GET',
        headers: {
        }
    })
        .then(response => {
            if (!response.ok) {
                console.log("history.js: response not ok");
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
                    <p>${new Date(game.start_time).toLocaleString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                    <p>${game.player1_username} - ${game.player2_username}</p>
                    <p>Winner: ${game.winner_name}</p>
                </div>
                `;
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