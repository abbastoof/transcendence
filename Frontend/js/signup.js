document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Bootstrap modal
    var signUpModal = new bootstrap.Modal(document.getElementById('signUpModal'));

    // Sign Up form submit event listener
    document.getElementById('signUpForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        // Get form values
        const email = document.getElementById('signUpEmail').value;
        const username = document.getElementById('signUpUsername').value;
        const password = document.getElementById('signUpPassword').value;
        const repeatPassword = document.getElementById('signUpRePassword').value;

        // Do something with the collected data (e.g., send it to a server)
        console.log('Sign Up - Email:', email);
        console.log('Sign Up - Username:', username);
        console.log('Sign Up - Password:', password);
        console.log('Sign Up - re-password:', repeatPassword);

        // Close the modal using Bootstrap modal method
        signUpModal.hide();

        // Reset the form fields
        this.reset();
    });

    // Reset form fields when modal is hidden (on modal close)
    signUpModal._element.addEventListener('hidden.bs.modal', function () {
        document.getElementById('signUpForm').reset();
    });
});


