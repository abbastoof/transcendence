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
