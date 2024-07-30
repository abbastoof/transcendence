import { createModal, createGameModal } from './createModal.js'
import { insert, insertModal } from './insert.js'
import { startGame } from './pong/pong.js'

insert('.headerContainer', 'headerSVG.html');
//insertModal('.tournament', 'tournamentModal.html', 'tournament', 'Tournament');

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

createModal('tournament', 'Tournament', `
    <form id="playerForm" class="form">
        <p class="font">Select number of players:</p>
        <div class="row justify-content-center">
                <div class="col-md-3">
                        <div class="form-check">
                                <input class="form-check-input" type="radio" name="playerCount" id="2vs2" value="2">
                                <label class="form-check-label font" for="2vs2">2</label>
                        </div>
                </div>
                <div class="col-md-3">
                        <div class="form-check">
                                <input class="form-check-input" type="radio" name="playerCount" id="4vs4" value="4">
                                <label class="form-check-label font" for="4vs4">4</label>
                        </div>
                </div>
                <div class="col-md-3">
                        <div class="form-check">
                                <input class="form-check-input" type="radio" name="playerCount" id="6vs6" value="6">
                                <label class="form-check-label font" for="6vs6">6</label>
                        </div>
                </div>
                <div class="col-md-3">
                        <div class="form-check">
                                <input class="form-check-input" type="radio" name="playerCount" id="8vs8" value="8">
                                <label class="form-check-label font" for="8vs8">8</label>
                        </div>
                </div>
        </div>
        <div id="playerAliasInputs" style="display: none;">
                <!-- Player alias inputs will be dynamically added here -->
        </div>
        <button type="submit" class="submit">Play</button>
    </form>`)
import './modals/tournament.js';

createModal('signUp', 'Sign up', `
    <form id="signUpForm" class="form">
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
createModal('login', 'Log in', `
            <form id="loginForm" class="form">
                <div class="form-group">
                    <label class="labelFont" for="loginUsername">Username</label>
                    <input type="text" class="form-control" id="loginUsername" placeholder="Enter username" required>
                </div>
                <div class="form-group">
                    <label class="labelFont" for="loginPassword">Password</label>
                    <input type="password" class="form-control" id="loginPassword" placeholder="Enter password" required>
                </div>
                <button type="submit" class="submit">Log in</button>
            </form>
        </div>
        <div class="row mt-3">
            <p class="font text-center">
                Don't have an account? <a href="#" class="signup-link" data-bs-dismiss="modal" data-bs-toggle="modal" data-bs-target="#signUpModal">Sign up</a>
            </p>`);
import './modals/signup.js';

createModal('logout', 'Log out', `
        <div class="modal-body">
            <p class="ErrorMessage">Are you sure you want to log out?</p>
        </div>
        <div class="modal-footer">
            <button type="button" class="submit" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="submit" onclick="confirmLogout()">Yes, Log out</button>
        </div>`);
import './modals/login.js';

insertModal('.about', 'aboutModal.html', 'about', 'About');

createModal('Profile', 'Profile', '<div id="userProfile"></div>')
