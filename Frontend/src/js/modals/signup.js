document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Bootstrap modal
    var signUpModalElement = document.getElementById('signUpModal');
    if (!signUpModalElement) {
        console.error('Sign Up modal element not found');
        return;
    }
        
    var modalTitle = document.getElementById('signUpLabel');
    var modalBody = document.querySelector('#signUpModal .modal-body');

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
            showErrorMessage('Passwords do not match!');
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
            document.getElementById('signupModal').querySelector('.close').click(); // Close the modal
            document.getElementById('signUpForm').reset();
        })
        .catch(error => {
            console.error('Error:', error);
            if (error.error) {
                if (error.error.username) {
                    showErrorMessage('Sign up failed: ' + error.error.username.join(' '));
                }
                if (error.error.email) {
                    showErrorMessage('Sign up failed: ' + error.error.email.join(' '));
                }
                if (error.error.password) {
                    showErrorMessage('Sign up failed: ' + error.error.password.join(' '));
                }
            } else {
                showErrorMessage('Sign up failed: Something went wrong');
            }
            clearPasswordFields();
        });
    });

    // Function to show error message
    function showErrorMessage(message) {
        // Remove any existing error message
        const existingErrorMessage = document.querySelector('#signUpModal .ErrorMessage');
        if (existingErrorMessage) {
            existingErrorMessage.remove();
        }

        // Create a span element for the error message
        var errorSpan = document.createElement('span');
        errorSpan.classList.add('ErrorMessage');
        errorSpan.textContent = message;

        // Insert the error message before the modal body
        modalBody.parentNode.insertBefore(errorSpan, modalBody);

        // Hide the error message after 5 seconds
        setTimeout(function() {
            if (errorSpan && errorSpan.parentNode) {
                errorSpan.parentNode.removeChild(errorSpan);
            }
        }, 3500);
    }

    // Function to clear password fields
    function clearPasswordFields() {
        document.getElementById('signUpPassword').value = '';
        document.getElementById('signUpRePassword').value = '';
    }
});
