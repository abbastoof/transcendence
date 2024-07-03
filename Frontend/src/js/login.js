/*

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Bootstrap modal
    var logInModal = new bootstrap.Modal(document.getElementById('logInModal'));

    // Login form submit event listener
    document.getElementById('logInForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get form values
        const username = document.getElementById('logInUsername').value;
        const password = document.getElementById('logInPassword').value;

        // Send data to the server
        fetch('https://localhost:3000/auth/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            alert('Logged in successful!');
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Log in failed!');
        });

        // Close the modal using Bootstrap modal method
        logInModal.hide();

        // Reset the form fields
        this.reset();
    });

    // Reset form fields when modal is hidden (on modal close)
    logInModal._element.addEventListener('hidden.bs.modal', function () {
        document.getElementById('logInForm').reset();
    });
});
*/

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Bootstrap modal
    var logInModal = new bootstrap.Modal(document.getElementById('logInModal'));
    var modalTitle = document.getElementById('logInModalLabel');
    var modalBody = document.querySelector('#logInModal .modal-body');

    // Check if modalTitle and modalBody elements exist
    if (!modalTitle || !modalBody) {
        console.error('Modal title or body element not found');
        return;
    }
    // Login form submit event listener
    document.getElementById('logInForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get form values
        const username = document.getElementById('logInUsername').value;
        const password = document.getElementById('logInPassword').value;

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
            logInModal.hide(); // Close the modal on success
            this.reset(); // Reset form fields
            localStorage.setItem('userData', JSON.stringify({ id: data.id, token: data.access }));
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
        const existingErrorMessage = document.querySelector('#logInModal .ErrorMessage');
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
        }, 2500);
    }

    // Function to clear password field
    function clearPasswordField() {
        document.getElementById('logInPassword').value = '';
    }

    // Reset form fields and hide error message when modal is hidden (on modal close)
    logInModal._element.addEventListener('hidden.bs.modal', function () {
        document.getElementById('logInForm').reset();
        // Remove any error messages
        const errorSpans = document.querySelectorAll('#logInModal .ErrorMessage');
        errorSpans.forEach(function(errorSpan) {
            errorSpan.remove();
        });
    });
});
