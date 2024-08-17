import { showMessage } from './messages.js';

// Function to toggle the email update form visibility
export function toggleEmailForm() {
    const updateEmailForm = document.getElementById('updateEmailForm');
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

        fetch(`/user/${userData.id}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${userData.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: newEmail })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Email updated successfully:', data);
            showMessage('Email updated successfully', '#ProfileModal', 'accept');
            document.getElementById('emailText').innerText = data.email;
            document.getElementById('newEmail').value = '';
            document.getElementById('updateEmailForm').style.display = 'none';
        })
        .catch(error => {
            console.error('Error updating email:', error);
            showMessage('Error updating email', '#ProfileModal', 'error');
            document.getElementById('newEmail').value = '';
        });
    });
}
