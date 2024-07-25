// Import our custom CSS
import '../../scss/styles.scss';

// Import all of Bootstrap's JS
import * as bootstrap from 'bootstrap';

export function updateUserProfile() {
    // Check if the user is logged in
    const userData = JSON.parse(localStorage.getItem('userData'));
    console.log('UserData:', userData); // Debugging line
    if (!userData || !userData.id || !userData.token) {
        console.error('UserData is missing or incomplete');
        return;
    }

    // Fetch user data from the server
    fetch(`/user/${userData.id}/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${userData.token}`
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Fetched Data:', data); // Debugging line
        const userProfileContainer = document.getElementById('userProfile');
        if (!userProfileContainer) {
            console.error('UserProfile container not found');
            return;
        }
        const htmlContent = `
            <div class="container mt-4">
                <div class="profile-header d-flex align-items-center">
                    <img id="avatar" src="${data.avatar || '/media/default.jpg'}" alt="User Profile Image" class="img-thumbnail mb-4 mr-3" width="80" height="80">
                    <h1 id="username" class="display-4">${data.username}</h1>
                </div>
                <p class="lead">Email: ${data.email}</p>
                <form id="imageUploadForm">
                    <div class="form-group">
                        <label for="imageInput" class="submit">Choose file</label>
                        <input type="file" id="imageInput" class="form-control-file" accept="image/*">
                    </div>
                    <button type="submit" class="submit btn btn-primary">Submit</button>
                </form>
            </div>
        `;
        userProfileContainer.innerHTML = htmlContent;

        const form = document.getElementById('imageUploadForm');
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            const imageInput = document.getElementById('imageInput');
            const file = imageInput.files[0];
            if (!file) {
                console.error('No image selected');
                return;
            }
            const formData = new FormData();
            formData.append("avatar", file);

            // Send the image data to the server
            fetch(`/user/${userData.id}/`, {
                method: 'PUT',
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
                // Update the user profile with the new image
                const avatar = document.getElementById('avatar');
                avatar.src = `${data.avatar}?t=${new Date().getTime()}`;
                avatar.onerror = () => {
                    console.error('Error loading new image.');
                    avatar.src = '/media/default.jpg'; // Fallback to default image
                };
            })
            .catch(error => {
                console.error('Error uploading image:', error);
            });
        });
    })
    .catch(error => {
        console.error('Error fetching user data:', error);
    });
}
