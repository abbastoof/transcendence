
document.addEventListener('DOMContentLoaded', function () {
	const userData = JSON.parse(localStorage.getItem('userData'));
	if (!userData || !userData.id || !userData.token) {
		console.error('UserData is missing or incomplete');
		return;
	}

	fetch(`/user/${userData.id}/friends`, {
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
		const friendsContainer = document.getElementById('friendsList');
		if (!friendsContainer) {
			console.error('Friends container not found');
			return;
		}
		let htmlContent = '<div class="container mt-4"><h2>Friends</h2>';
		data.forEach(friend => {
			htmlContent += `
			<div class="friend-record mb-3">
				<h3>${friend.name}</h3>
				<p>Status: ${friend.isOnline ? 'Online' : 'Offline'}</p>
				<button onclick="sendMessage('${friend.id}')">Send Message</button>
			</div>
			`;
		});
		htmlContent += '</div>';
		friendsContainer.innerHTML = htmlContent;
	})
	.catch(error => {
		console.error('Error fetching friends:', error);
	});
});

function sendMessage(friendId) {
	const message = prompt("Enter your message:");
	if (message) {
		// Implement the fetch request to send the message to the server
		console.log(`Message to send to ${friendId}: ${message}`);
		// Example:
		// fetch(`/send-message`, { method: 'POST', body: JSON.stringify({ friendId, message }) })
	}
}