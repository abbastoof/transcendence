import { updateFriendsList } from './friends.js';
import { updateMatchHistory } from './history.js';
import { handleTokenVerification } from '../tokenHandler.js';
import { toggleEmailForm, handleEmailUpdate } from './changeEmail.js';
import { togglePasswordForm, handlePasswordUpdate } from './changePassword.js';
import { toggleProfilePictureForm, handleProfilePictureUpdate } from './changeProfilePicture.js';
import { showMessage } from './messages.js';

function resetProfileForms() {
    document.getElementById('updateEmailForm').style.display = 'none';
    document.getElementById('updatePasswordForm').style.display = 'none';
    document.getElementById('imageUploadForm').style.display = 'none';

    document.getElementById('newEmail').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('imageInput').value = '';
    document.getElementById('fileName').textContent = 'No file chosen';
}

document.addEventListener('DOMContentLoaded', function () {
    updateUserProfile();

    const profileModal = document.getElementById('ProfileModal');
    if (profileModal) {
        profileModal.addEventListener('hide.bs.modal', resetProfileForms);
    }
});

export function updateUserProfile() {
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData || !userData.id || !userData.token) {
        return;
    }

    const fetchProfile = (userData) => {
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
                const userProfileContainer = document.getElementById('userProfile');
                if (!userProfileContainer) {
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
                        <input type="email" maxlength="50" id="newEmail" class="form-control" placeholder="Enter new email" required>
                    </div>
                    <button type="submit" class="submit">Update Email</button>
                </form>
                <form id="emailVerificationForm" style="display: none;">
                    <div class="verification">
                        <label for="emailVerificationCode" class="labelFont">Verification Code</label>
                        <input type="text" maxlength="6" class="form-control" id="emailVerificationCode" placeholder="Enter code" required>
                    </div>
                    <div class="modal-footer">
                        <button type="submit" class="submit">Verify</button>
                        <button type="button" id="emailCancelVerificationButton" class="submit">Cancel</button>
                    </div>
                </form>
                <button id="changePasswordButton" class="submit">Change Password</button>
                <form class="form" id="updatePasswordForm" style="display:none;">
                    <div class="form-group">
                        <label class="labelFont" for="newPassword">New Password</label>
                        <input type="password" maxlength="50" id="newPassword" class="form-control" placeholder="Enter new password" required>
                    </div>
                    <button type="submit" class="submit">Update Password</button>
                </form>
                <button id="changeProfilePictureButton" class="submit">Change Profile Picture</button>
                <form class="form" id="imageUploadForm" style="display:none;">
                    <div class="form-group-image">
                        <label for="imageInput" class="submit">Choose file</label>
                        <input type="file" id="imageInput" accept="image/*">
                        <span id="fileName" class="file-name">No file chosen</span>
                    </div>
                    <button type="submit" class="submit">Submit</button>
                </form>
                <button type="button" id="friendsButton" class="submit" data-bs-toggle="modal" data-bs-target="#FriendsModal">Friends</button>
                <button type="button" id="matchHistoryButton" class="submit" data-bs-toggle="modal" data-bs-target="#HistoryModal">Match history</button>
                <!-- 2FA Toggle Switch -->
                <div class="toggle-container">
                    <label class="toggle-label">Two-Factor Authentication:</label>
                    <label class="switch">
                        <input type="checkbox" id="twoFactorAuthToggle" ${data.otp_status ? 'checked' : ''}>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>`;
                userProfileContainer.innerHTML = htmlContent;

                updateFriendsList();
                updateMatchHistory();

                // Initialize event handlers
                document.getElementById('changeEmailButton').addEventListener('click', toggleEmailForm);
                handleEmailUpdate(userData);

                document.getElementById('changePasswordButton').addEventListener('click', togglePasswordForm);
                handlePasswordUpdate(userData);

                document.getElementById('changeProfilePictureButton').addEventListener('click', toggleProfilePictureForm);
                handleProfilePictureUpdate(userData);
                
                document.getElementById('friendsButton').addEventListener('click', updateFriendsList);

                document.getElementById('matchHistoryButton').addEventListener('click', updateMatchHistory);
                // Handle 2FA Toggle Switch
                document.getElementById('twoFactorAuthToggle').addEventListener('change', function () {
                    toggleTwoFactorAuth(userData, this.checked);
                });

            })
            .catch(error => {
                showMessage('Error fetching user profile', '#ProfileModal', 'error');
            });
    }
    handleTokenVerification()
        .then(validToken => {
            userData.token = validToken;
            fetchProfile(userData);

        })
        .catch(error => {
            showMessage(`Error verifying token: ${error.message}`, '#ProfileModal', 'error');
        });

    // Function to toggle 2FA status on the server
    function toggleTwoFactorAuth(userData, isEnabled) {
        handleTokenVerification()
        .then(validToken => {
            return fetch(`/user/${userData.id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${validToken}`
                },
                body: JSON.stringify({ otp_status: isEnabled ? "True" : "False" })
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update 2FA status');
            }
            return response.json();
        })
        .then(data => {
            showMessage('2FA status updated successfully', '#ProfileModal', 'accept');
        })
        .catch(error => {
            showMessage('Error updating 2FA status', error, '#ProfileModal', 'error');
        });
    }
}
