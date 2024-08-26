import { updateUserProfile } from './profile.js';
import { showMessage } from './messages.js';
import { handleTokenVerification } from '../tokenHandler.js';
import { updateAuthButton } from './buttons.js';

// Main entry point for the authentication logic
document.addEventListener('DOMContentLoaded', function () {
    var loginModalElement = document.getElementById('loginModal');
    var loginForm = document.getElementById('loginForm');
    
    const isLoggedIn = sessionStorage.getItem('isLoggedIn') === 'true';

    // Attach login event handler
    loginForm.addEventListener('submit', handleLogin);

    // Assign confirmLogout function to be globally accessible
    window.confirmLogout = confirmLogout;

    // Initialize auth button state based on login status
    updateAuthButton(isLoggedIn);

    loginModalElement.addEventListener('hidden.bs.modal', function () {
        loginForm.reset();
        document.getElementById('loginVerification').style.display = 'none';
        document.getElementById('loginForm').style.display = 'flex';
    });

    document.getElementById('cancelLoginVerificationButton').addEventListener('click', function() {
        document.getElementById('loginForm').style.display = 'flex';
        document.getElementById('loginPassword').value = '';
        document.getElementById('loginVerification').style.display = 'none';
        document.getElementById('loginVerificationCode').value = '';
    });
});

export function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    fetch('/user/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, password: password }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Invalid username or password');
        }
        return response.json();
    })
    .then(data => {
        if (data.detail && data.detail === 'Verification password sent to your email') {
            // Show OTP verification form
            document.getElementById('loginVerification').style.display = 'block';
            document.getElementById('loginForm').style.display = 'none';
            showMessage('Verification code sent to your email', '#loginModal', 'accept');

            // Attach event listener for OTP verification
            document.getElementById('loginVerification').addEventListener('submit', event => handleOtpVerification(event, username, password));
        } else {
            completeLogin(data);
        }
    })
    .catch(error => {
        showMessage('Log in failed: ' + error.message, '#loginModal', 'error');
        clearPasswordField();
    });
}

function handleOtpVerification(event, username, password) {
    event.preventDefault();

    const otp = document.getElementById('loginVerificationCode').value;

    fetch('/user/login/verifyotp/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, password: password, otp: otp }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Invalid OTP');
        }
        return response.json();
    })
    .then(data => {
        completeLogin(data);
    })
    .catch(error => {
        showMessage('OTP verification failed: ' + error.message, '#loginModal', 'error');
        document.getElementById('loginVerificationCode').value = '';
    });
}

function completeLogin(data) {
    document.getElementById('loginVerificationCode').value = '';
    showMessage('Login successful', '#loginModal', 'accept');
    sessionStorage.setItem('userData', JSON.stringify({ id: data.id, token: data.access, refresh: data.refresh }));
    sessionStorage.setItem('isLoggedIn', 'true');
    history.replaceState(null, null, window.location.pathname);
    setTimeout(() => {
        document.getElementById('loginModal').querySelector('.close').click();
        document.getElementById('loginForm').reset();
        document.getElementById('loginVerification').style.display = 'none';
    }, 2500);

    // Call to update the auth button and add necessary buttons
    updateAuthButton(true);

    // Update user profile, assuming it's part of UI update
    updateUserProfile();
}

export function confirmLogout() {
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    if (!userData) {
        console.error('No user data found in sessionStorage.');
        return;
    }
    const sendLogoutRequest = (token) => {
    fetch(`/user/${userData.id}/logout/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Logout failed');
        }

        sessionStorage.clear();

        updateAuthButton(false);
        history.replaceState(null, null, window.location.pathname);
        document.getElementById('logoutModal').querySelector('.close').click();
    })
    .catch(error => {
        showMessage('Logout failed: ' + error.message, '#logoutModal', 'error');
    });
};
        // Handle token verification and refreshing
        handleTokenVerification()
        .then(validToken => {
            // Proceed with logout using the valid token
            sendLogoutRequest(validToken);
        })
        .catch(error => {
            showMessage('Logout failed: ' + error.message, '#logoutModal', 'error');
        });
}

function clearPasswordField() {
    document.getElementById('loginPassword').value = '';
}
