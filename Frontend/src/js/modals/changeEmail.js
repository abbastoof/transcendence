import { showMessage } from './messages.js';

// Function to toggle the email update form visibility
export function toggleEmailForm() {
    const updateEmailForm = document.getElementById('updateEmailForm');
    const emailVerificationForm = document.getElementById('emailVerificationForm');

    // Block toggle if the verification form is open
    if (emailVerificationForm.style.display === 'block') {
        console.log('Cannot toggle email form while verification form is open');
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
            console.error('Email cannot be empty');
            return;
        }
        console.log('New email:', newEmail);
        // Check if the new email is available
        fetch('/user/register/availableuser/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userData.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: newEmail })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Email is already in use');
            }
            return response.json();
        })
        .then(() => {
            // Send OTP to the new email
            return fetch('/user/register/sendemailotp/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${userData.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: newEmail })
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to send OTP');
            }
            return response.json();
        })
        .then(() => {
            console.log('OTP sent successfully');
            showMessage('OTP sent to your new email', '#ProfileModal', 'accept');
            document.getElementById('updateEmailForm').style.display = 'none';
            document.getElementById('emailVerificationForm').style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error sending verification code', '#ProfileModal', 'error');
        });
    });

    document.getElementById('emailVerificationForm').addEventListener('submit', (event) => {
        event.preventDefault();
        const newEmail = document.getElementById('newEmail').value;
        const otp = document.getElementById('emailVerificationCode').value;
        if (!otp) {
            console.error('OTP cannot be empty');
            return;
        }

        // Verify the OTP
        fetch('/user/register/verifyemailotp/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userData.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: newEmail, otp: otp })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Invalid OTP');
            }
            return response.json();
        })
        .then(() => {
            // Update the email in the backend
            return fetch(`/user/${userData.id}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${userData.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: newEmail })
            });
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update email');
            }
            return response.json();
        })
        .then(data => {
            console.log('Email updated successfully:', data);
            showMessage('Email updated successfully', '#ProfileModal', 'accept');
            document.getElementById('emailText').innerText = data.email;
            document.getElementById('newEmail').value = '';
            document.getElementById('emailVerificationCode').value = '';
            document.getElementById('emailVerificationForm').style.display = 'none';
        })
        .catch(error => {
            console.error('Error verifying OTP:', error);
            showMessage('Error verifying OTP', '#ProfileModal', 'error');
        });
    });

    // Add event listener for the cancel button
    document.getElementById('emailCancelVerificationButton').addEventListener('click', () => {
        document.getElementById('emailVerificationForm').style.display = 'none';
        document.getElementById('updateEmailForm').style.display = 'flex';
    });
}