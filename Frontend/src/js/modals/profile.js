import { updateFriendsList } from './friends.js';
import { showMessage } from './messages.js';
import { updateMatchHistory } from './history.js';

document.addEventListener('DOMContentLoaded', function () {
    const userProfileModal = document.getElementById('ProfileModal');
    userProfileModal.addEventListener('show.bs.modal', updateUserProfile);
});


export function updateUserProfile() {
    // Check if the user is logged in
    const userData = JSON.parse(localStorage.getItem('userData'));
    console.log('UserData:', userData); // Debugging line
    console.log('UserData token:', userData.token); // Debugging line
    if (!userData || !userData.id || !userData.token) {
        console.error('UserData is missing or incomplete');
        return;
    }

    // Fetch user data from the server
    fetch(`/user/${userData.id}/`, {
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
        console.log('Fetched Data:', data); // Debugging line
        const userProfileContainer = document.getElementById('userProfile');
        if (!userProfileContainer) {
            console.error('UserProfile container not found');
            return;
        }
        const htmlContent = `
            <div class="container">
                <div class="profile-header">
                    <img id="avatar" src="${data.avatar || '/media/default.jpg'}" alt="User Profile Image" style="height: auto;" width="80" height="80">
                    <h1 id="username" class="display-4 user-font">&nbsp;${data.username}</h1>
                </div>
                <p class="lead font">Email:&nbsp;<span class="font" id="emailText">${data.email}</span></p>
                <button id="changeEmailButton" class="submit">Change Email</button>
                <form class="form" id="updateEmailForm" style="display:none;">
                    <div class="form-group">
                        <label class="labelFont" for="newEmail">New Email</label>
                        <input type="email" id="newEmail" class="form-control" placeholder="Enter new email" required>
                    </div>
                    <button type="submit" class="submit">Update Email</button>
                </form>
                <button id="changePasswordButton" class="submit">Change Password</button>
                <form class="form" id="updatePasswordForm" style="display:none;">
                    <div class="form-group">
                        <label class="labelFont" for="newPassword">New Password</label>
                        <input type="password" id="newPassword" class="form-control" placeholder="Enter new password" required>
                    </div>
                    <button type="submit" class="submit">Update Password</button>
                </form>
                <button id="changeProfilePictureButton" class="submit">Change Profile Picture</button>
                <form class="form" id="imageUploadForm" style="display:none;">
                    <div class="form-group-image">
                        <label for="imageInput" class="submit">Choose file</label>
                        <input type="file" id="imageInput">
                        <span id="fileName" class="file-name">No file chosen</span>
                    </div>
                    <button type="submit" class="submit">Submit</button>
                </form>
                <button type="button" class="submit" data-bs-toggle="modal" data-bs-target="#FriendsModal">Friends</button>
                <button type="button" class="submit" data-bs-toggle="modal" data-bs-target="#HistoryModal">Match history</button>
            </div>
        `;
        userProfileContainer.innerHTML = htmlContent;

        updateFriendsList(); // Ensure this function is not modifying the HTML in unexpected ways
        updateMatchHistory();

        // Toggle email update form visibility
        document.getElementById('changeEmailButton').addEventListener('click', () => {
            const updateEmailForm = document.getElementById('updateEmailForm');
            if (updateEmailForm.style.display === 'none' || updateEmailForm.style.display === '') {
                updateEmailForm.style.display = 'flex';
                updateEmailForm.style.flexDirection = 'column';
            } else {
                updateEmailForm.style.display = 'none';
            }
        });

        // Handle email update
        document.getElementById('updateEmailForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const newEmail = document.getElementById('newEmail').value;
            if (!newEmail) {
                console.error('Email cannot be empty');
                return;
            }

            fetch(`/user/${userData.id}/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${userData.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: newEmail })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Email updated successfully:', data);
                showMessage('Email updated successfully', '#ProfileModal', 'accept');
                document.getElementById('emailText').innerText = data.email;
                document.getElementById('newEmail').value = '';
                document.getElementById('updateEmailForm').style.display = 'none';
            })
            .catch(error => {
                console.error('Error updating email:', error);
                showMessage('Error updating email', '#ProfileModal', 'error');

            });
        });

        // Toggle password update form visibility
        document.getElementById('changePasswordButton').addEventListener('click', () => {
            const updatePasswordForm = document.getElementById('updatePasswordForm');
            if (updatePasswordForm.style.display === 'none' || updatePasswordForm.style.display === '') {
                updatePasswordForm.style.display = 'flex';
                updatePasswordForm.style.flexDirection = 'column';
            } else {
                updatePasswordForm.style.display = 'none';
            }
        });

        // Handle password update
        document.getElementById('updatePasswordForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const newPassword = document.getElementById('newPassword').value;
            if (!newPassword) {
                console.error('Password cannot be empty');
                return;
            }

            fetch(`/user/${userData.id}/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${userData.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ password: newPassword })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Password updated successfully:', data);
                showMessage('Password updated successfully', '#ProfileModal', 'accept');
                document.getElementById('newPassword').value = '';
                document.getElementById('updatePasswordForm').style.display = 'none';
            })
            .catch(error => {
                console.error('Error updating password:', error);
                showMessage('Error updating password', '#ProfileModal', 'error');
                document.getElementById('newPassword').value = '';
            });
        });

        // Toggle profile picture update form visibility
        document.getElementById('changeProfilePictureButton').addEventListener('click', () => {
            const imageUploadForm = document.getElementById('imageUploadForm');
            if (imageUploadForm.style.display === 'none' || imageUploadForm.style.display === '') {
                imageUploadForm.style.display = 'flex';
                imageUploadForm.style.flexDirection = 'column';
            } else {
                imageUploadForm.style.display = 'none';
            }
        });

        document.getElementById('imageInput').addEventListener('change', (event) => {
            const fileInput = event.target;
            const fileNameDisplay = document.getElementById('fileName');
            if (fileInput.files.length > 0) {
                fileNameDisplay.textContent = fileInput.files[0].name;
            } else {
                fileNameDisplay.textContent = 'No file chosen';
            }
        });

        // Handle image upload
        document.getElementById('imageUploadForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const imageInput = document.getElementById('imageInput');
            const file = imageInput.files[0];
            if (!file) {
                console.error('No image selected');
                showMessage('No image selected', '#ProfileModal', 'error');
                return;
            }
            const formData = new FormData();
            formData.append('avatar', file);

            fetch(`/user/${userData.id}/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${userData.token}`
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Image uploaded successfully:', data);
                showMessage('Profile picture updated successfully', '#ProfileModal', 'accept');
                document.getElementById('avatar').src = `${data.avatar}?t=${new Date().getTime()}`;
                document.getElementById('imageUploadForm').style.display = 'none';
                document.getElementById('fileName').textContent = 'No file chosen';
            })
            .catch(error => {
                console.error('Error uploading image:', error);
                showMessage('Error uploading image', '#ProfileModal', 'error');
            });
        });
    })
    .catch(error => {
        console.error('Error fetching user data:', error);
    });
}
