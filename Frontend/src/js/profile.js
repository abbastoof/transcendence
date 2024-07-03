document.addEventListener('DOMContentLoaded', function() {
    const userData = JSON.parse(localStorage.getItem('userData'));
    console.log('UserData:', userData); // Debugging line
    if (!userData || !userData.id || !userData.token) {
        console.error('UserData is missing or incomplete');
        return;
    }

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
                <div>What'sup biatch</div>
            `;
            userProfileContainer.innerHTML = htmlContent;
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
    // avatar, username, friends, dm, email, change password