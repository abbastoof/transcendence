// Function to refresh the token
function refreshTokenRequest(userData) {
    return fetch('/auth/token/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userData.refreshToken}`
        },
        body: JSON.stringify({ id: userData.id })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Token refresh failed');
        }
        return response.json();
    })
    .then(data => {
        // Update userData with new tokens
        userData.token = data.token;
        userData.refreshToken = data.refreshToken;
        sessionStorage.setItem('userData', JSON.stringify(userData));
        return data.token;
    });
}

// Function to verify the token on the backend
function verifyToken(userData) {
    return fetch('/auth/token/validate-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: userData.id, access: userData.token, is_frontend: true })
    })
    .then(response => {
        if (response.ok) {
            return true; // Token is valid
        } else if (response.status === 401) {
            return false; // Token is expired
        } else {
            throw new Error('Token verification failed');
        }
    });
}

export function handleTokenVerification() {
    let userData = JSON.parse(sessionStorage.getItem('userData'));
    return verifyToken(userData)
    .then(isValid => {
        if (isValid) {
            return userData.token; // Token is valid
        } else {
            // Token is expired, refresh the token
            return refreshTokenRequest(userData);
        }
    });
}