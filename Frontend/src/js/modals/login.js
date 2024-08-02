import * as bootstrap from 'bootstrap';
import { updateUserProfile } from './profile.js';
import { openWaitingLobby } from './playonline.js';

document.addEventListener('DOMContentLoaded', function () {
    var loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    var logoutModal = new bootstrap.Modal(document.getElementById('logoutModal'));
    var authButton = document.getElementById('authButton');

    // Check localStorage for login state and tokens
    var isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

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
            localStorage.setItem('userData', JSON.stringify({ id: data.id, token: data.access, refresh: data.refresh }));
            localStorage.setItem('isLoggedIn', 'true'); // Save login state to localStorage

            loginModal.hide(); // Close the modal on success
            document.getElementById('loginForm').reset(); // Reset form fields
            isLoggedIn = true; // Update login state
            updateAuthButton();
            addProfileButton(); // Add profile button on login
            addPlayOnlineButton(); // Add play online button on login
            updateUserProfile();
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Log in failed: ' + error.message);
            clearPasswordField();
        });
    });

    // Function to show error message
    function showErrorMessage(message) {
        // Remove any existing error message
        const existingErrorMessage = document.querySelector('#loginModal .ErrorMessage');
        if (existingErrorMessage) {
            existingErrorMessage.remove();
        }

        // Create a span element for the error message
        var errorSpan = document.createElement('span');
        errorSpan.classList.add('ErrorMessage');
        errorSpan.textContent = message;

        // Insert the error message before the modal body
        var modalBody = document.querySelector('#loginModal .modal-body');
        modalBody.parentNode.insertBefore(errorSpan, modalBody);

        // Hide the error message after 5 seconds
        setTimeout(function () {
            if (errorSpan && errorSpan.parentNode) {
                errorSpan.parentNode.removeChild(errorSpan);
            }
        }, 2500);
    }

    // Function to clear password field
    function clearPasswordField() {
        document.getElementById('loginPassword').value = '';
    }

    // Reset form fields and hide error message when modal is hidden (on modal close)
    loginModal._element.addEventListener('hidden.bs.modal', function () {
        document.getElementById('loginForm').reset();
        // Remove any error messages
        const errorSpans = document.querySelectorAll('#loginModal .ErrorMessage');
        errorSpans.forEach(function (errorSpan) {
            errorSpan.remove();
        });
    });

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
        var userData = JSON.parse(localStorage.getItem('userData'));
        if (!userData) {
            console.error('No user data found in localStorage.');
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

            localStorage.clear(); // Clear all localStorage items

            isLoggedIn = false; // Update login state
            localStorage.setItem('isLoggedIn', 'false'); // Save login state to localStorage
            updateAuthButton();
            logoutModal.hide();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };

    // Initially update the button and profile button
    updateAuthButton();
});
