import { showMessage } from './messages.js';

document.addEventListener('DOMContentLoaded', function() {
    var signUpModalElement = document.getElementById('signUpModal');
    var modalTitle = document.getElementById('signUpLabel');
    var signUpForm = document.getElementById('signUpForm');
    var verificationForm = document.getElementById('verificationForm');
    var cancelVerificationButton = document.getElementById('cancelVerificationButton');

    signUpModalElement.addEventListener('hidden.bs.modal', function () {
        signUpForm.reset();
        verificationForm.reset();
        showSignUpForm(); // Reset modal to initial state
    });

    signUpForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const email = document.getElementById('signUpEmail').value;
        const username = document.getElementById('signUpUsername').value;
        const password = document.getElementById('signUpPassword').value;
        const repeatPassword = document.getElementById('signUpRePassword').value;

        if (password !== repeatPassword) {
            showMessage('Passwords do not match!', '#signUpModal', 'error');
            clearPasswordFields();
            return;
        }

        // Simulate a successful server response
        simulateServerResponse(true);
    });

    verificationForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const verificationCode = document.getElementById('verificationCode').value;

        // Simulate a verification response
        simulateVerificationResponse(true);
    });

    // Add event listener for the cancel button
    cancelVerificationButton.addEventListener('click', function() {
        showSignUpForm();
    });

    function simulateServerResponse(success) {
        if (success) {
            showVerificationForm();
        } else {
            showMessage('Sign up failed: Something went wrong', '#signUpModal', 'error');
        }
    }

    function simulateVerificationResponse(success) {
        if (success) {
            showMessage('Verification successful!', '#signUpModal', 'success');
            history.back(); // Simulate redirect or other success action
        } else {
            showMessage('Verification failed: Invalid code', '#signUpModal', 'error');
        }
    }

    function showVerificationForm() {
        modalTitle.textContent = 'Enter Verification Code';
        signUpForm.style.display = 'none';
        verificationForm.style.display = 'block';
    }

    function showSignUpForm() {
        modalTitle.textContent = 'Sign Up';
        signUpForm.style.display = 'flex';
        verificationForm.style.display = 'none';
    }

    function clearPasswordFields() {
        document.getElementById('signUpPassword').value = '';
        document.getElementById('signUpRePassword').value = '';
    }

    // Initial call to ensure the modal starts with the sign-up form
    showSignUpForm();
});
