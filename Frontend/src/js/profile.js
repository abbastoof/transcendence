document.addEventListener('DOMContentLoaded', function () {
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
                    <h1 id="username" class="display-4">${data.username}</h1>
                    <p class="lead">Email: ${data.email}</p>
                    <img id="avatar" src="../assets/images/avatar.jpg" alt="User Profile Image" class="img-thumbnail mb-4" width="60" height="60">
                    <form id="imageUploadForm">
                        <div class="form-group">
                            <label for="imageInput" class="submit">Choose file</label>
                            <input type="file" id="imageInput" class="form-control-file" accept="image/*" hidden>
                        </div>
                        <button type="submit" class="submit">Submit</button>
                    </form>
                </div>
            `;
            userProfileContainer.innerHTML = htmlContent;
            // <img src="${data.imageUrl}" alt="User Profile Image">

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
                formData.append('image', file);

                // Send the image data to the server
                fetch(`/user/${userData.id}/image`, {
                    method: 'POST',
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
                        const userProfileImage = document.createElement('img');
                        userProfileImage.src = data.imageUrl;
                        userProfileContainer.appendChild(userProfileImage);
                    })
                    .catch(error => {
                        console.error('Error uploading image:', error);
                    });
            });
        })
});