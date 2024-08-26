import { showMessage } from './messages.js';
import { isStrongPassword, clearPasswordFields } from './password.js';

document.addEventListener('DOMContentLoaded', function() {
    var signUpModalElement = document.getElementById('signUpModal');
    var signUpForm = document.getElementById('signUpForm');
    var verificationForm = document.getElementById('verificationForm');
    
    let email, username, password, repeatPassword;

    signUpModalElement.addEventListener('hidden.bs.modal', function () {
        document.getElementById('loginForm').reset();
        signUpForm.reset();
        verificationForm.style.display = 'none';
        signUpForm.style.display = 'flex';
    });

    signUpForm.addEventListener('submit', function(event) {
        event.preventDefault();

        email = document.getElementById('signUpEmail').value;
        username = document.getElementById('signUpUsername').value;
        password = document.getElementById('signUpPassword').value;
        repeatPassword = document.getElementById('signUpRePassword').value;

        if (password !== repeatPassword) {
            showMessage('Passwords do not match!', '#signUpModal', 'error');
            clearPasswordFields();
            return;
        }

        if (!isStrongPassword(password).isValid) {
            showMessage(isStrongPassword(password).message, '#signUpModal', 'error');
            clearPasswordFields();
            return;
        }

        fetch('/user/register/availableuser/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, email: email })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                return fetch('/user/register/sendemailotp/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email }),
                });
            } else {
                clearPasswordFields();
                throw new Error(data.error);
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.detail && data.detail !== 'This email already verified.') {
                signUpForm.style.display = 'none';
                verificationForm.style.display = 'block';
                showMessage('Verification code sent to your email', '#signUpModal', 'accept');
            } else {
                showMessage('Failed to send verification email: ' + data.error, '#signUpModal', 'error');
            }
        })
        .catch(error => {
            showMessage(error.message || 'Failed to send verification email: Something went wrong', '#signUpModal', 'error');
        });
    });

    verificationForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const otp = document.getElementById('verificationCode').value;

        fetch('/user/register/verifyemailotp/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, otp: otp })
        })
        .then(response => response.json())
        .then(data => {
            if (data.detail && data.detail === 'Email verified') {
                return fetch('/user/register/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: username, email: email, password: password })
                });
            } else {
                throw new Error('Verification failed: ' + data.error);
            }
        })
        .then(response => response.json())
        .then(data => {
            showMessage('Registration successful', '#signUpModal', 'accept');
            document.getElementById('verificationCode').value = '';
            setTimeout(() => {
                signUpModalElement.querySelector('.close').click();
            }, 2500);
        })
        .catch(error => {
            showMessage(error.message || 'Something went wrong', '#signUpModal', 'error');
            document.getElementById('verificationCode').value = '';
        });
    });

    document.getElementById('cancelVerificationButton').addEventListener('click', function() {
        signUpForm.style.display = 'flex';
        verificationForm.style.display = 'none';
        document.getElementById('verificationCode').value = '';
        document.getElementById('signUpPassword').value = '';
        document.getElementById('signUpRePassword').value = '';
    });
});