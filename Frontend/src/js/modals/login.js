import { updateUserProfile } from './profile.js';
import { openWaitingLobby } from './playonline.js';
import { showMessage } from './messages.js';

document.addEventListener('DOMContentLoaded', function () {
    var authButton = document.getElementById('authButton');

    // Check sessionStorage for login state and tokens
    var isLoggedIn = sessionStorage.getItem('isLoggedIn') === 'true';

    // Reset form fields and hide error message when modal is hidden
    loginModal.addEventListener('hidden.bs.modal', function () {
        loginForm.reset(); // Reset all form fields
    });

    // Function to create and add the profile button
    function addProfileButton() {
        var buttonContainer = document.querySelector('.buttonContainer');
        if (!document.getElementById('profileButton')) { // Check if profile button already exists
            var profileButton = document.createElement('button');
            profileButton.type = 'button';
            profileButton.className = 'buttons';
            profileButton.id = 'profileButton';
            profileButton.textContent = 'Profile';
            profileButton.setAttribute('data-bs-toggle', 'modal');
            profileButton.setAttribute('data-bs-target', '#ProfileModal');
            buttonContainer.appendChild(profileButton);
            // Insert profile button before the about button
            buttonContainer.insertBefore(profileButton, buttonContainer.children[3]);
        }
    }

    // Function to create and add the play online button
    function addPlayOnlineButton() {
        var buttonContainer = document.querySelector('.buttonContainer');
        if (!document.getElementById('playOnlineButton')) { // Check if play online button already exists
            var playOnlineButton = document.createElement('button');
            playOnlineButton.type = 'button';
            playOnlineButton.className = 'buttons';
            playOnlineButton.id = 'playOnlineButton';
            playOnlineButton.textContent = 'Play Online';
            playOnlineButton.addEventListener('click', openWaitingLobby); // Add event listener to open the waiting lobby
            buttonContainer.appendChild(playOnlineButton);
            // Insert play online button before the about button
            buttonContainer.insertBefore(playOnlineButton, buttonContainer.children[0]);
        }
    }

    // Function to remove the profile button
    function removeProfileButton() {
        var profileButton = document.getElementById('profileButton');
        if (profileButton) {
            profileButton.parentNode.removeChild(profileButton);
        }
    }

    // Function to remove the play online button
    function removePlayOnlineButton() {
        var playOnlineButton = document.getElementById('playOnlineButton');
        if (playOnlineButton) {
            playOnlineButton.parentNode.removeChild(playOnlineButton);
        }
    }

    // Login form submit event listener
    document.getElementById('loginForm').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form submission

        // Get form values
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        // Send data to the server
        fetch('/user/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Invalid username or password');
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            // Store all tokens and user ID
            sessionStorage.setItem('userData', JSON.stringify({ id: data.id, token: data.access, refresh: data.refresh }));
            sessionStorage.setItem('isLoggedIn', 'true'); // Save login state to sessionStorage

            //loginModal.hide(); // Close the modal on success
            document.getElementById('loginModal').querySelector('.close').click(); // Close the modal on success
            document.getElementById('loginForm').reset(); // Reset form fields
            isLoggedIn = true; // Update login state
            updateAuthButton();
            addProfileButton(); // Add profile button on login
            addPlayOnlineButton(); // Add play online button on login
            updateUserProfile();
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Log in failed: ' + error.message, '#loginModal', 'error');
            clearPasswordField();
        });
    });

    // Function to clear password field
    function clearPasswordField() {
        document.getElementById('loginPassword').value = '';
    }

    // Reset form fields and hide error message when modal is hidden (on modal close)



    // Function to update the auth button
    function updateAuthButton() {
        if (isLoggedIn) {
            authButton.textContent = 'Log out';
            authButton.setAttribute('data-bs-toggle', 'modal');
            authButton.setAttribute('data-bs-target', '#logoutModal');
            addProfileButton(); // Ensure profile button is added
            addPlayOnlineButton(); // Ensure play online button is added
        } else {
            authButton.textContent = 'Log in';
            authButton.setAttribute('data-bs-toggle', 'modal');
            authButton.setAttribute('data-bs-target', '#loginModal');
            removeProfileButton(); // Remove profile button if logged out
            removePlayOnlineButton(); // Remove play online button if logged out
        }
    }

    // Function to handle logout confirmation
    window.confirmLogout = function () {
        var userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData) {
            console.error('No user data found in sessionStorage.');
            return;
        }

        fetch(`/user/${userData.id}/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + userData.token
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Logout failed');
            }
            console.log('Logout successful');

            sessionStorage.clear(); // Clear all sessionStorage items

            isLoggedIn = false; // Update login state
            sessionStorage.setItem('isLoggedIn', 'false'); // Save login state to sessionStorage
            history.replaceState(null, null, window.location.pathname);
            document.getElementById('logoutModal').querySelector('.close').click(); // Close the modal on success
            updateAuthButton();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };

    // Initially update the button and profile button
    updateAuthButton();
});
