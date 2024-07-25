import '../../scss/styles.scss';

document.addEventListener('DOMContentLoaded', function () {
	updateFriendsList();
});

export function updateFriendsList() {
	const userData = JSON.parse(localStorage.getItem('userData'));
	if (!userData || !userData.id || !userData.token) {
		console.error('UserData is missing or incomplete');
		return;
	}

	fetch(`/user/${userData.id}/friends/`, {
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
			let htmlContent = `
			<div class="container mt-4"><h2>Friends</h2>
			<form id="friendForm" class="text-center">
                <div class="form-group">
                    <label class="labelFont" for="friendID">friend ID</label>
                    <input type="text" class="form-control" id="friendID" placeholder="Enter friend ID" required>
                </div>
                <button type="submit" class="submit">Send request</button>
            </form>
			</div>`;
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
		.then(() => {
			const form = document.getElementById('friendForm');
			form.addEventListener('submit', function (event) {
				event.preventDefault(); // Prevent form submission
				sendFriendRequest(userData);
			});
		})
		.catch(error => {
			console.error('Error fetching friends:', error);
		});
};

function sendFriendRequest(userData) {
    const friendID = document.getElementById('friendID').value;
    // Ensure friendID is validated and sanitized here

    fetch(`/user/${userData.id}/request/${friendID}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${userData.token}`
        }
    })
    .then(response => {
        if (response.ok) {
            alert('Friend request sent!');
        } else {
            alert('Failed to send friend request.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function sendMessage(friendId) {
	const message = prompt("Enter your message:");
	if (message) {
		// Implement the fetch request to send the message to the server
		console.log(`Message to send to ${friendId}: ${message}`);
		// Example:
		// fetch(`/send-message`, { method: 'POST', body: JSON.stringify({ friendId, message }) })
	}
}