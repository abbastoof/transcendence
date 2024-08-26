import { showMessage } from './messages.js';
import { handleTokenVerification } from '../tokenHandler.js'; // Import your token verification function

// Function to toggle the email update form visibility
export function toggleEmailForm() {
    const updateEmailForm = document.getElementById('updateEmailForm');
    const emailVerificationForm = document.getElementById('emailVerificationForm');

    // Block toggle if the verification form is open
    if (emailVerificationForm.style.display === 'block') {
        return;
    }
    if (updateEmailForm.style.display === 'none' || updateEmailForm.style.display === '') {
        updateEmailForm.style.display = 'flex';
        updateEmailForm.style.flexDirection = 'column';
    } else {
        updateEmailForm.style.display = 'none';
    }
}

// Function to handle the email update process
export function handleEmailUpdate(userData) {
    document.getElementById('updateEmailForm').addEventListener('submit', (event) => {
        event.preventDefault();
        const newEmail = document.getElementById('newEmail').value;
        if (!newEmail) {
            showMessage('Email cannot be empty', '#ProfileModal', 'error');
            return;
        }

        handleTokenVerification().then(token => {
            // Check if the new email is available
            return fetch('/user/register/availableuser/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: newEmail })
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Email is already in use');
            }
            return response.json();
        })
        .then(() => {
            // Send OTP to the new email
            return handleTokenVerification().then(token => {
                return fetch('/user/register/sendemailotp/', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: newEmail })
                });
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to send OTP');
            }
            return response.json();
        })
        .then(() => {
            showMessage('OTP sent to your new email', '#ProfileModal', 'accept');
            document.getElementById('updateEmailForm').style.display = 'none';
            document.getElementById('emailVerificationForm').style.display = 'block';
        })
        .catch(error => {
            showMessage('Error sending verification code', error, '#ProfileModal', 'error');
        });
    });

    document.getElementById('emailVerificationForm').addEventListener('submit', (event) => {
        event.preventDefault();
        const newEmail = document.getElementById('newEmail').value;
        const otp = document.getElementById('emailVerificationCode').value;
        if (!otp) {
            showMessage('Verification code cannot be empty', '#ProfileModal', 'error');
            return;
        }

        handleTokenVerification().then(token => {
            // Verify the OTP
            return fetch('/user/register/verifyemailotp/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: newEmail, otp: otp })
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Invalid OTP');
            }
            return response.json();
        })
        .then(() => {
            // Update the email in the backend
            return handleTokenVerification().then(token => {
                return fetch(`/user/${userData.id}/`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: newEmail })
                });
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update email');
            }
            return response.json();
        })
        .then(data => {
            showMessage('Email updated successfully', '#ProfileModal', 'accept');
            document.getElementById('emailText').innerText = data.email;
            document.getElementById('newEmail').value = '';
            document.getElementById('emailVerificationCode').value = '';
            document.getElementById('emailVerificationForm').style.display = 'none';
        })
        .catch(error => {
            showMessage('Error verifying OTP', error, '#ProfileModal', 'error');
        });
    });

    // Add event listener for the cancel button
    document.getElementById('emailCancelVerificationButton').addEventListener('click', () => {
        document.getElementById('emailVerificationForm').style.display = 'none';
        document.getElementById('updateEmailForm').style.display = 'flex';
    });
}
