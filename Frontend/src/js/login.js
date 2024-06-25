document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Bootstrap modal
    var logInModal = new bootstrap.Modal(document.getElementById('logInModal'));

    // Login form submit event listener
    document.getElementById('logInForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get form values
        const username = document.getElementById('logInUsername').value;
        const password = document.getElementById('logInPassword').value;

        // Do something with the collected data (e.g., send it to a server)
        console.log('Log in - Username:', username);
        console.log('Log in - Password:', password);

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
