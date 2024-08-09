import {showMessage} from './messages.js';

document.addEventListener('DOMContentLoaded', function () {
    const friendsModal = document.getElementById('FriendsModal');
    friendsModal.addEventListener('show.bs.modal', updateFriendsList);
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
			<div class="container">
			<form id="friendForm">
                <div class="form-group">
                    <label class="font" for="friendUsername">Add friend</label>
                    <input type="text" class="form-control" id="friendUsername" placeholder="Enter username" required>
					<button type="submit" class="submit">Send request</button>
				</div>
            </form>
			<h2 class="font">Friends list</h2>
			`;

			data.forEach(friend => {
				htmlContent += `
				<div class="friend-record">
					<p class="font">${friend.username}: <span class="${friend.status ? 'online' : 'offline'}">&nbsp;${friend.status ? 'Online' : 'Offline'}</span>
					<button class="remove-btn reject" data-friend-id="${friend.id}">Remove</button>
					</p>
				</div>
				`;
			});
			htmlContent += '</div>';
			friendsContainer.innerHTML = htmlContent;

			document.querySelectorAll('.remove-btn').forEach(button => {
				button.addEventListener('click', function () {
					removeFriend(userData, this.getAttribute('data-friend-id'));
				});
			});

			getPendingFriendRequests(userData);
		})
		.then(() => {
			const form = document.getElementById('friendForm');
			form.addEventListener('submit', function (event) {
				event.preventDefault();
				sendFriendRequest(userData);
			});
		})
		.catch(error => {
			console.error('Error fetching friends:', error);
		});
};

function sendFriendRequest(userData) {
	const friendUsername = document.getElementById('friendUsername').value;
	if (friendUsername === userData.username) {
		showMessage('You cannot send a friend request to yourself', '#FriendsModal', 'error');
		throw new Error('You cannot send a friend request to yourself');
	}
	fetch(`/user/${userData.id}/request/`, {
		method: 'POST',
		headers: {
			'Authorization': `Bearer ${userData.token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ "username": friendUsername }),
	})
		.then(response => {
			if (response.ok) {
				return response.json();
			} else {
				return response.json().then(errorData => {
					throw new Error(errorData.error || 'Something went wrong');
				});
			}
		})
		.then(data => {
			showMessage(data.detail, '#FriendsModal', 'accept');
		})
		.catch(error => {
			showMessage(`Error sending friend request: ${error.message}`, '#FriendsModal', 'error');
		});
}

function getPendingFriendRequests(userData) {
	fetch(`/user/${userData.id}/pending/`, {
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
			const pendingContainer = document.getElementById('pendingList');
			if (!pendingContainer) {
				console.error('Pending container not found');
				return;
			}
			console.log(data);
			let htmlContent = `<div class="container"><h2 class="font">Pending friend requests</h2>`;
			data.forEach(pending => {
				htmlContent += `
                <div class="pending-request">
                    <h2 class="font">User: ${pending.sender_username}
                    <button class="accept-btn submit accept-button" data-pending-sender_user="${pending.sender_id}">Accept</button>
					<button class="reject-btn reject" data-pending-sender_user="${pending.sender_id}">Reject</button>
					</h2>
					</div>
            `;
			});
			htmlContent += '</div>';
			pendingContainer.innerHTML = htmlContent;
			document.querySelectorAll('.accept-btn').forEach(button => {
				button.addEventListener('click', function () {
					acceptPendingFriendRequest(userData, this.getAttribute('data-pending-sender_user'));
				});
			});
			document.querySelectorAll('.reject-btn').forEach(button => {
				button.addEventListener('click', function () {
					rejectPendingFriendRequest(userData, this.getAttribute('data-pending-sender_user'));
				});
			});
		})
		.catch(error => {
			console.error('Error fetching pending:', error);
		});
}

function acceptPendingFriendRequest(userData, requestID) {
	fetch(`/user/${userData.id}/accept/${requestID}/`, {
		method: 'PUT',
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
			showMessage('Friend request accepted', '#FriendsModal', 'accept');
			updateFriendsList();
		})
		.catch(error => {
			console.error('Error accepting friend request:', error);
		});
}

function rejectPendingFriendRequest(userData, requestID) {
	fetch(`/user/${userData.id}/reject/${requestID}/`, {
		method: 'PUT',
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
			showMessage('Friend request rejected', '#FriendsModal', 'error');
			updateFriendsList();
		})
		.catch(error => {
			console.error('Error rejecting friend request:', error);
		});
}

function removeFriend(userData, friendID) {
    fetch(`/user/${userData.id}/friends/${friendID}/remove/`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${userData.token}` }
    })
    .then(response => {
        if (response.status === 204) {
            showMessage('Friend removed successfully', '#FriendsModal', 'accept');
            updateFriendsList();
        } else if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(errData.error || 'Network response was not ok');
            });
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data) {
            showMessage('Friend removed:', data, '#FriendsModal', 'accept');
            updateFriendsList();
        }
    })
    .catch(error => {
        console.error('Error removing friend:', error);
    });
};
