import { updateAuthButton } from "./modals/buttons";

// Function to refresh the token
function refreshTokenRequest(userData) {
    return fetch('/auth/token/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userData.refresh}`
        },
        body: JSON.stringify({ id: userData.id })
    })
    .then(response => {
        if (!response.ok) {
            alert('Session expired. Please login again.');
            sessionStorage.clear();
            updateAuthButton(false);
            window.location.replace('');
        }
        return response.json();
    })
    .then(data => {
        // Update userData with new tokens
        userData.token = data.access;
        sessionStorage.setItem('userData', JSON.stringify(userData));
        return userData.token;
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