// Import our custom CSS
import '../scss/styles.scss'
import { createModal, createGameModal } from './createModal.js'
import { insert, insertModal } from './insert.js'
import { startGame } from './pong/pong.js'

// Import all of Bootstrap's JS
import * as bootstrap from 'bootstrap'

insert('.headerContainer', 'headerSVG.html');
insertModal('.tournament', 'tournamentModal.html', 'tournament');

const gameModal = createGameModal();
// Select the button that should open the game modal
console.log(gameModal)
console.log(typeof gameModal.show); // Check if the show method is a function

const gameButton = document.querySelector('button[data-bs-target="#pongModal"]');

if (gameButton) {
    // Add an event listener to the button
    gameButton.addEventListener('click', (event) => {
        console.log('Game button clicked');
        // Prevent the default Bootstrap modal from opening
        event.preventDefault();

        // Open the game modal
        gameModal.show();
    });
} else {
    console.error('Game button not found');
}


document.getElementById('pongModal').addEventListener('shown.bs.modal', function() {
    setTimeout(startGame(), 0);
});

createModal('signUp', `
    <form id="signUpForm">
        <div class="form-group">
        <label class="labelFont" for="signUpEmail">Email</label>
            <input type="email" class="form-control" id="signUpEmail" placeholder="Enter email"
                required>
        </div>
        <div class="form-group">
            <label class="labelFont" for="signUpUsername">Username</label>
            <input type="text" class="form-control" id="signUpUsername" placeholder="Enter username"
                required>
        </div>
        <div class="form-group">
            <label class="labelFont" for="signUpPassword">Password</label>
            <input type="password" class="form-control" id="signUpPassword" placeholder="Enter password"
                required>
        </div>
        <div class="form-group">
            <label class="labelFont" for="signUpRePassword">Re-enter Password</label>
            <input type="password" class="form-control" id="signUpRePassword"
                placeholder="Re-enter password" required>
        </div>
        <button type="submit" class="submit">Sign up</button>
    </form>`)
import './modals/signup.js';

import './modals/profile.js';
createModal('login', `
            <form id="loginForm" class="text-center">
                <div class="form-group">
                    <label class="labelFont" for="loginUsername">Username</label>
                    <input type="text" class="form-control" id="loginUsername" placeholder="Enter username" required>
                </div>
                <div class="form-group">
                    <label class="labelFont" for="loginPassword">Password</label>
                    <input type="password" class="form-control" id="loginPassword" placeholder="Enter password" required>
                </div>
                <button type="submit" class="submit btn btn-primary">Log in</button>
            </form>
        </div>
        <div class="row mt-3">
            <p class="font text-center">
                Don't have an account? <a href="#" class="signup-link" data-bs-dismiss="modal" data-bs-toggle="modal" data-bs-target="#signUpModal">Sign up</a>
            </p>`);
import './modals/signup.js';

createModal('logout', `
        <div class="modal-body">
            <p class="ErrorMessage">Are you sure you want to log out?</p>
        </div>
        <div class="submitContainer">
            <button type="button" class="submit" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="submit" onclick="confirmLogout()">Yes, Log out</button>
        </div>`);
import './modals/login.js';

insertModal('.about', 'aboutModal.html', 'about');

createModal('Profile', '<div id="userProfile"></div>')

