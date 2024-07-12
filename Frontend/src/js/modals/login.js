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
        fetch('https://localhost:3000/auth/login/', {
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
                localStorage.setItem('isLoggedIn', 'true'); // Save login state to localStorage ! change this to variable in backend

                loginModal.hide(); // Close the modal on success
                document.getElementById('loginForm').reset(); // Reset form fields
                isLoggedIn = true; // Update login state
                updateAuthButton();
                addProfileButton(); // Add profile button on login
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
        } else {
            authButton.textContent = 'Log in';
            authButton.setAttribute('data-bs-toggle', 'modal');
            authButton.setAttribute('data-bs-target', '#loginModal');
            removeProfileButton(); // Remove profile button if logged out
        }
    }

    // Function to handle logout confirmation
    window.confirmLogout = function () {
        // Simulating a successful logout response
        console.log('Logout successful: Simulated response');
        userId = null; // Clear user ID
        refreshToken = null; // Clear refresh token
        accessToken = null; // Clear access token

        localStorage.clear('userData'); // Clear all localStorage items

        isLoggedIn = false; // Update login state
        localStorage.setItem('isLoggedIn', 'false'); // Save login state to localStorage
        updateAuthButton();
        logoutModal.hide();
    };

    // Initially update the button and profile button
    updateAuthButton();
});
