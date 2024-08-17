import { showMessage } from './messages.js';

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
            console.error('No image selected');
            showMessage('No image selected', '#ProfileModal', 'error');
            return;
        }
        const formData = new FormData();
        formData.append('avatar', file);

        fetch(`/user/${userData.id}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${userData.token}`
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
            console.log('Image uploaded successfully:', data);
            showMessage('Profile picture updated successfully', '#ProfileModal', 'accept');
            document.getElementById('avatar').src = `${data.avatar}?t=${new Date().getTime()}`;
            document.getElementById('imageUploadForm').style.display = 'none';
            document.getElementById('imageInput').value = '';
            document.getElementById('fileName').textContent = 'No file chosen';
        })
        .catch(error => {
            console.error('Error uploading image:', error);
            showMessage('Error uploading image', '#ProfileModal', 'error');
            document.getElementById('imageInput').value = '';
            document.getElementById('fileName').textContent = 'No file chosen';
        });
    });
}
