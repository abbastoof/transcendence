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
                    <label class="labelFont" for="friendUsername">friend Username</label>
                    <input type="text" class="form-control" id="friendUsername" placeholder="Enter friend username" required>
                </div>
                <button type="submit" class="submit">Send request</button>
            </form>`;
			data.forEach(friend => {
				htmlContent += `
			<div class="friend-record mb-3">
				<h3>${friend.username}</h3>
				<p>Status: ${friend.status ? 'Online' : 'Offline'}</p>
				<button class="remove-btn" data-friend-id="${friend.id}">Remove friend</button>
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
		alert('You cannot send a friend request to yourself');
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
			alert(data.detail);
		})
		.catch(error => {
			alert(`Error sending friend request: ${error.message}`);
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
			let htmlContent = `<div class="container mt-4"><h2>Pending friend requests</h2>`;
			data.forEach(pending => {
				htmlContent += `
                <div class="pending-request mb-3">
                    <h3>User: ${pending.sender_username}</h3>
                    <button class="accept-btn" data-pending-sender_user="${pending.sender_id}">Accept friend request</button>
					<button class="reject-btn" data-pending-sender_user="${pending.sender_id}">Reject friend request</button>
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
			alert('Friend request accepted');
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
			alert('Friend request rejected');
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
            alert('Friend removed successfully');
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
            alert('Friend removed:', data);
            updateFriendsList();
        }
    })
    .catch(error => {
        console.error('Error removing friend:', error);
    });
};