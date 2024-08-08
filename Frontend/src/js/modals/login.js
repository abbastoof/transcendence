import { updateUserProfile } from './profile.js';

document.addEventListener('DOMContentLoaded', function () {
    var authButton = document.getElementById('authButton');

    // Check sessionStorage for login state and tokens
    var isLoggedIn = sessionStorage.getItem('isLoggedIn') === 'true';

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

    // Function to remove the profile button
    function removeProfileButton() {
        var profileButton = document.getElementById('profileButton');
        if (profileButton) {
            profileButton.parentNode.removeChild(profileButton);
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
                sessionStorage.setItem('isLoggedIn', 'true'); // Save login state to sessionStorage ! change this to variable in backend

                document.getElementById('loginModal').querySelector('.close').click(); // Close the modal

                document.getElementById('loginForm').reset(); // Reset form fields
                isLoggedIn = true; // Update login state
                updateAuthButton();
                addProfileButton(); // Add profile button on login
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

    // Function to update the auth button
    function updateAuthButton() {
        if (isLoggedIn) {
            authButton.textContent = 'Log out';
            authButton.setAttribute('data-bs-toggle', 'modal');
            authButton.setAttribute('data-bs-target', '#logoutModal');
            addProfileButton(); // Ensure profile button is added
        } else {
            authButton.textContent = 'Log in';
            authButton.setAttribute('data-bs-toggle', 'modal');
            authButton.setAttribute('data-bs-target', '#loginModal');
            removeProfileButton(); // Remove profile button if logged out
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

                document.getElementById('logoutModal').querySelector('.close').click(); // Close the modal

                updateAuthButton();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    };

    // Initially update the button and profile button
    updateAuthButton();
});
