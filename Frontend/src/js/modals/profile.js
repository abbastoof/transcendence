import { updateFriendsList } from './friends.js';

document.addEventListener('DOMContentLoaded', function () {
    updateUserProfile();
});

export function updateUserProfile() {
    // Check if the user is logged in
    const userData = JSON.parse(localStorage.getItem('userData'));
    console.log('UserData:', userData); // Debugging line
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
            <div class="container mt-4">
                <div class="profile-header d-flex align-items-center">
                    <img id="avatar" src="${data.avatar || '/media/default.jpg'}" alt="User Profile Image" class="img-thumbnail mb-4 mr-3" width="80" height="80">
                    <h1 id="username" class="display-4">${data.username}</h1>
                </div>
                <p class="lead">Email: <span id="emailText">${data.email}</span></p>
                <button id="changeEmailButton" class="submit">Change Email</button>
                <form id="updateEmailForm" class="mt-3" style="display:none;">
                    <div class="form-group">
                        <label for="newEmail">New Email</label>
                        <input type="email" id="newEmail" class="form-control" placeholder="Enter new email">
                    </div>
                    <button type="submit" class="submit">Update Email</button>
                </form>
                <button id="changePasswordButton" class="submit">Change Password</button>
                <form id="updatePasswordForm" class="mt-3" style="display:none;">
                    <div class="form-group">
                        <label for="newPassword">New Password</label>
                        <input type="password" id="newPassword" class="form-control" placeholder="Enter new password">
                    </div>
                    <button type="submit" class="submit">Update Password</button>
                </form>
                <button id="changeProfilePictureButton" class="submit">Change Profile Picture</button>
                <form id="imageUploadForm" class="mt-3" style="display:none;">
                    <div class="form-group">
                        <label for="imageInput" class="submit">Choose file</label>
                        <input type="file" id="imageInput" class="form-control-file" accept="image/*">
                    </div>
                    <button type="submit" class="submit">Submit</button>
                </form>
                <button type="button" class="buttons" data-bs-toggle="modal" data-bs-target="#FriendsModal">Friends</button>
            </div>
        `;
        userProfileContainer.innerHTML = htmlContent;

        updateFriendsList(); // Ensure this function is not modifying the HTML in unexpected ways

        // Toggle email update form visibility
        document.getElementById('changeEmailButton').addEventListener('click', () => {
            document.getElementById('updateEmailForm').style.display = 
                document.getElementById('updateEmailForm').style.display === 'none' ? 'block' : 'none';
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
                document.getElementById('emailText').innerText = data.email;
                document.getElementById('updateEmailForm').style.display = 'none';
            })
            .catch(error => {
                console.error('Error updating email:', error);
            });
        });

        // Toggle password update form visibility
        document.getElementById('changePasswordButton').addEventListener('click', () => {
            document.getElementById('updatePasswordForm').style.display = 
                document.getElementById('updatePasswordForm').style.display === 'none' ? 'block' : 'none';
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
                alert('Password updated successfully');
                document.getElementById('updatePasswordForm').style.display = 'none';
            })
            .catch(error => {
                console.error('Error updating password:', error);
            });
        });

        // Toggle profile picture update form visibility
        document.getElementById('changeProfilePictureButton').addEventListener('click', () => {
            document.getElementById('imageUploadForm').style.display = 
                document.getElementById('imageUploadForm').style.display === 'none' ? 'block' : 'none';
        });

        // Handle image upload
        document.getElementById('imageUploadForm').addEventListener('submit', (event) => {
            event.preventDefault();
            const imageInput = document.getElementById('imageInput');
            const file = imageInput.files[0];
            if (!file) {
                console.error('No image selected');
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
                document.getElementById('avatar').src = `${data.avatar}?t=${new Date().getTime()}`;
                document.getElementById('imageUploadForm').style.display = 'none';
            })
            .catch(error => {
                console.error('Error uploading image:', error);
            });
        });

    })
    .catch(error => {
        console.error('Error fetching user data:', error);
    });
}
