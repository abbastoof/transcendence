import { showMessage } from './messages.js';
import { handleTokenVerification } from '../tokenHandler.js';// Import your token verification function

// Function to toggle the profile picture update form visibility
export function toggleProfilePictureForm() {
    const imageUploadForm = document.getElementById('imageUploadForm');
    if (imageUploadForm.style.display === 'none' || imageUploadForm.style.display === '') {
        imageUploadForm.style.display = 'flex';
        imageUploadForm.style.flexDirection = 'column';
    } else {
        imageUploadForm.style.display = 'none';
    }
}

// Function to handle the profile picture update process
export function handleProfilePictureUpdate(userData) {
    document.getElementById('imageInput').addEventListener('change', (event) => {
        const fileInput = event.target;
        const fileNameDisplay = document.getElementById('fileName');
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = fileInput.files[0].name;
        } else {
            fileNameDisplay.textContent = 'No file chosen';
        }
    });

    document.getElementById('imageUploadForm').addEventListener('submit', (event) => {
        event.preventDefault();
        const imageInput = document.getElementById('imageInput');
        const file = imageInput.files[0];
        if (!file) {
            showMessage('No image selected', '#ProfileModal', 'error');
            return;
        }
        const fileType=file.type;
        if (file) {
            const fileType=file.type;
            const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/jpg'];
            if (!validImageTypes.includes(file.type)) {
                showMessage('Please upload a valid image file.', '#ProfileModal', 'error');
                return
            }
        }
        const formData = new FormData();
        formData.append('avatar', file);

        // Verify token and update it if necessary
        handleTokenVerification().then(token => {
            fetch(`/user/${userData.id}/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                showMessage('Profile picture updated successfully', '#ProfileModal', 'accept');
                document.getElementById('avatar').src = `${data.avatar}?t=${new Date().getTime()}`;
                document.getElementById('imageUploadForm').style.display = 'none';
                document.getElementById('imageInput').value = '';
                document.getElementById('fileName').textContent = 'No file chosen';
            })
            .catch(error => {
                showMessage('Error uploading image', '#ProfileModal', 'error');
                document.getElementById('imageInput').value = '';
                document.getElementById('fileName').textContent = 'No file chosen';
            });
        })
        .catch(error => {
            showMessage('Session expired. Please log in again.', error, '#ProfileModal', 'error');
        });
    });
}
