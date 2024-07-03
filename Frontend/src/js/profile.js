const userData = JSON.parse(localStorage.getItem('userData'));
fetch(`/user/${userData.username}`, {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${userData.token}`
    }
})
    .then(response => response.json())
    .then(data => {
        // Store all JSON fields of the response
        // You can access the fields using the 'data' variable
        // For example, if the response has a field called 'name', you can access it like this:
        const name = data.name;
        // Store the other fields in a similar way
    })
    .catch(error => {
        // Handle any errors that occur during the request
        console.error('Error:', error);
    });