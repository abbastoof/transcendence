import { showMessage } from './messages.js';

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Bootstrap modal
    var signUpModalElement = document.getElementById('signUpModal');
    if (!signUpModalElement) {
        console.error('Sign Up modal element not found');
        return;
    }
    
    var modalTitle = document.getElementById('signUpLabel');
    var modalBody = document.querySelector('#signUpModal .modal-body');
    var signUpForm = document.getElementById('signUpForm');
    
    signUpModalElement.addEventListener('hidden.bs.modal', function () {
        signUpForm.reset(); // Reset all form fields
    });

    // Check if modalTitle and modalBody elements exist
    if (!modalTitle || !modalBody) {
        console.error('Modal title or body element not found');
        return;
    }

    // Sign Up form submit event listener
    document.getElementById('signUpForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get form values
        const email = document.getElementById('signUpEmail').value;
        const username = document.getElementById('signUpUsername').value;
        const password = document.getElementById('signUpPassword').value;
        const repeatPassword = document.getElementById('signUpRePassword').value;

        // Check if passwords match
        if (password !== repeatPassword) {
            showMessage('Passwords do not match!', '#signUpModal', 'error');
            clearPasswordFields();
            return;
        }

        // Send data to the server
        fetch('/user/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, username, password }),
        })
        .then(response => {
            return response.json().then(data => {
                if (!response.ok) {
                    throw data;
                }
                return data;
            });
        })
        .then(data => {
            console.log('Success:', data);
            history.back();
            document.getElementById('signUpForm').reset();
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.error) {
                for (let key in error.error) {
                    if (error.error.hasOwnProperty(key)) {
                        let errorMessage = error.error[key];
                        if (Array.isArray(errorMessage)) {
                            errorMessage = errorMessage.join(' ');
                        }
                        showMessage('Sign up failed: ' + errorMessage, '#signUpModal', 'error');
                    }
                }
                if (error.error.password) {
                    showErrorMessage('Sign up failed: ' + error.error.password.join(' '));
                }
            } else {
                showMessage('Sign up failed: Something went wrong', '#signUpModal', 'error');
            }
            clearPasswordFields();
        });
    });

    // Function to clear password fields
    function clearPasswordFields() {
        document.getElementById('signUpPassword').value = '';
        document.getElementById('signUpRePassword').value = '';
    }
});
