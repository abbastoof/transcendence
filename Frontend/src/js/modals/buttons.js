import { openWaitingLobby } from './playonline.js';

export function addProfileButton() {
    const buttonContainer = document.querySelector('.buttonContainer');
    if (!document.getElementById('profileButton')) {
        const profileButton = document.createElement('button');
        profileButton.type = 'button';
        profileButton.className = 'buttons';
        profileButton.id = 'profileButton';
        profileButton.textContent = 'Profile';
        profileButton.setAttribute('data-bs-toggle', 'modal');
        profileButton.setAttribute('data-bs-target', '#ProfileModal');
        buttonContainer.appendChild(profileButton);
        buttonContainer.insertBefore(profileButton, buttonContainer.children[3]);
    }
}

export function addPlayOnlineButton() {
    const buttonContainer = document.querySelector('.buttonContainer');
    if (!document.getElementById('playOnlineButton')) {
        const playOnlineButton = document.createElement('button');
        playOnlineButton.type = 'button';
        playOnlineButton.className = 'buttons';
        playOnlineButton.id = 'playOnlineButton';
        playOnlineButton.textContent = 'Play Online';
        playOnlineButton.addEventListener('click', openWaitingLobby);
        buttonContainer.appendChild(playOnlineButton);
        buttonContainer.insertBefore(playOnlineButton, buttonContainer.children[0]);
    }
}

export function removeProfileButton() {
    const profileButton = document.getElementById('profileButton');
    if (profileButton) {
        profileButton.parentNode.removeChild(profileButton);
    }
}

export function removePlayOnlineButton() {
    const playOnlineButton = document.getElementById('playOnlineButton');
    if (playOnlineButton) {
        playOnlineButton.parentNode.removeChild(playOnlineButton);
    }
}

export function updateAuthButton(isLoggedIn) {
    const authButton = document.getElementById('authButton');
    if (isLoggedIn) {
        authButton.textContent = 'Log out';
        authButton.setAttribute('data-bs-toggle', 'modal');
        authButton.setAttribute('data-bs-target', '#logoutModal');
        addProfileButton();
        addPlayOnlineButton();
    } else {
        authButton.textContent = 'Log in';
        authButton.setAttribute('data-bs-toggle', 'modal');
        authButton.setAttribute('data-bs-target', '#loginModal');
        removeProfileButton();
        removePlayOnlineButton();
    }
}
