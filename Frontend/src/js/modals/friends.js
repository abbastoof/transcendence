import { showMessage } from './messages.js';
import { handleTokenVerification } from '../tokenHandler.js';

document.addEventListener('DOMContentLoaded', function () {
	updateFriendsList();

	const friendsModal = document.getElementById('FriendsModal');
	if (friendsModal) {
		friendsModal.addEventListener('hide.bs.modal', clearAddFriendForm);
	}
});

export function updateFriendsList() {
	const userData = JSON.parse(sessionStorage.getItem('userData'));
	if (!userData || !userData.id || !userData.token) {
		return;
	}

	const fetchFriends = (userData) => {
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
					showMessage('Friends container not found', '#FriendsModal', 'error');
					return;
				}

				let htmlContent = `
			<div class="container">
			<form id="friendForm">
                <div class="form-group">
                    <label class="font" for="friendUsername">Add friend</label>
                    <input type="text" maxlength="50" class="form-control" id="friendUsername" placeholder="Enter username" required>
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
						handleTokenVerification()
						.then(validToken => {
							userData.token = validToken;
							removeFriend(userData, this.getAttribute('data-friend-id'));
						})
						.catch(error => {
							showMessage(`Error removing friend: ${error.message}`, '#FriendsModal', 'error');
						});
					});
				});

				handleTokenVerification()
					.then(validToken => {
						userData.token = validToken;
						getPendingFriendRequests(userData);
					})
					.catch(error => {
						showMessage(`Error verifying token: ${error.message}`, '#FriendsModal', 'error');
					});

			})
			.then(() => {
				const form = document.getElementById('friendForm');
				form.addEventListener('submit', function (event) {
					event.preventDefault();

					handleTokenVerification()
						.then(validToken => {
							userData.token = validToken;
							sendFriendRequest(userData);
						})
						.catch(error => {
							showMessage(`Error verifying token: ${error.message}`, '#FriendsModal', 'error');
						});

				});
			})
			.catch(error => {
				showMessage(`Error fetching friends: ${error.message}`, '#FriendsModal', 'error');
			});
	};

	handleTokenVerification()
		.then(validToken => {
			userData.token = validToken;
			fetchFriends(userData);
		})
		.catch(error => {
			showMessage(`Error verifying token: ${error.message}`, '#FriendsModal', 'error');
		});

};

function sendFriendRequest(userData) {
	const friendUsername = document.getElementById('friendUsername').value;
	if (friendUsername === userData.username) {
		showMessage('You cannot send a friend request to yourself', '#FriendsModal', 'error');
		document.getElementById('friendUsername').value = '';
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
			document.getElementById('friendUsername').value = '';
		})
		.catch(error => {
			showMessage(`Error sending friend request: ${error.message}`, '#FriendsModal', 'error');
			document.getElementById('friendUsername').value = '';
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
					handleTokenVerification()
						.then(validToken => {
							userData.token = validToken;
							acceptPendingFriendRequest(userData, this.getAttribute('data-pending-sender_user'));
						})
						.catch(error => {
							showMessage(`Error verifying token: ${error.message}`, '#FriendsModal', 'error');
						});
				});
			});
			document.querySelectorAll('.reject-btn').forEach(button => {
				button.addEventListener('click', function () {
					handleTokenVerification()
						.then(validToken => {
							userData.token = validToken;
							rejectPendingFriendRequest(userData, this.getAttribute('data-pending-sender_user'));
						})
						.catch(error => {
							showMessage(`Error verifying token: ${error.message}`, '#FriendsModal', 'error');
						});
				});
			});
		})
		.catch(error => {
			showMessage(`Error fetching pending requests: ${error.message}`, '#FriendsModal', 'error');
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
			showMessage('Error accepting friend request:', error, '#FriendsModal', 'error');
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
			showMessage('Error rejecting friend request:', error, '#FriendsModal', 'error');
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
			showMessage('Error removing friend:', error, '#FriendsModal', 'error');
		});
};

function clearAddFriendForm() {
    const friendForm = document.getElementById('friendForm');
    if (friendForm) {
        friendForm.reset(); // This will clear all input fields within the form
    }
}