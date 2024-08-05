document.addEventListener('DOMContentLoaded', function () {
	const userData = JSON.parse(localStorage.getItem('userData'));
	if (!userData || !userData.id || !userData.token) {
		console.error('UserData is missing or incomplete');
		return;
	}

	fetch(`/user/${userData.id}/game-history`, {
		method: 'GET',
		headers: {
			'Authorization': `Bearer ${userData.token}`
		}
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		const gameHistoryContainer = document.getElementById('gameHistory');
		if (!gameHistoryContainer) {
			console.error('GameHistory container not found');
			return;
		}
		let htmlContent = '<div class="container mt-4"><h2>Game History</h2>';
		data.forEach(game => {
			htmlContent += `
			<div class="game-record mb-3">
				<h3>${game.name}</h3>
				<p>Outcome: ${game.outcome}</p>
				<p>Date Played: ${new Date(game.datePlayed).toLocaleDateString()}</p>
			</div>
			`;
		});
		htmlContent += '</div>';
		gameHistoryContainer.innerHTML = htmlContent;
	})
	.catch(error => {
		console.error('Error fetching game history:', error);
	});
});