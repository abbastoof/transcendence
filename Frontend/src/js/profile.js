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
            <h1>${data.username}</h1>
            <p>Email: ${data.email}</p>
            <form id="form">What'sup biatch</form>
            `;
            userProfileContainer.innerHTML = htmlContent;
        
            // Now that the form is guaranteed to exist, modify it and add the event listener
            const form = document.getElementById('form');
            form.innerHTML += `
                <input type="file" id="imageInput" accept="image/*">
                <button type="submit">Submit</button>
            `;
        
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