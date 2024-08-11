import '../scss/styles.scss'
import * as bootstrap from 'bootstrap'
import { createModal } from './createModal.js'
import { insert, insertModal } from './insert.js'
import './pong/pong.js'
import './modals/signup.js';
import './modals/profile.js';
import './modals/login.js';
import './modals/tournament.js';
import './modals/friends.js';




insert('.headerContainer', 'headerSVG.html');
//insertModal('.tournament', 'tournamentModal.html', 'tournament', 'Tournament');

// // Assuming you have imported gnecessary modules and functions like startGame, cleanupGame
// document.addEventListener('DOMContentLoaded', function () {
//     // Initialize the modal with options to prevent closing on backdrop click
//     const pongModalElement = document.getElementById('pongModal');
//     const pongModal = new bootstrap.Modal(pongModalElement, {
//         backdrop: 'static',
//         keyboard: true // Optional: prevents closing with ESC key
//     });

//     // Show the modal and start the game when it's opened
//     pongModalElement.addEventListener('shown.bs.modal', function () {
//         startGame('pongGameContainer');
//     });

//     // Clean up game resources when the modal is closed
//     pongModalElement.addEventListener('hidden.bs.modal', function () {
//         cleanUpGame();
//     });

//     // Optionally, add event listeners for other modals if needed
// });

// document.addEventListener('DOMContentLoaded', function () {
//     // Initialize the modal with options to prevent closing on backdrop click
//     const pongModalElement = document.getElementById('pongModal');
//     const pongModal = new bootstrap.Modal(pongModalElement, {
//         backdrop: 'static',
//         keyboard: true // Optional: prevents closing with ESC key
//     });

//     // Show the modal and start the game when it's opened
//     pongModalElement.addEventListener('shown.bs.modal', function () {
//         startGame('pongGameContainer');
//     });

//     // Clean up game resources when the modal is closed
//     pongModalElement.addEventListener('hidden.bs.modal', function () {
//         cleanUpGame();
//     });
//     // Make modal available globally if needed
//     window.pongModal = pongModal;
//     // Optionally, add event listeners for other modals if needed
// });

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('startGameButton').addEventListener('click', function () {
        const gameId = document.getElementById('gameId').value.trim();
        const playerId1 = document.getElementById('playerId1').value.trim();
        const playerId2 = document.getElementById('playerId2').value.trim();

        if (!gameId || !playerId1 || !playerId2) {
            console.error('Please provide a game ID and both player IDs.');
            return;
        }

        // Call the function from playonline.js
        import('./modals/playonline.js').then(module => {
            module.startRemoteGame(gameId, [playerId1, playerId2]);
        });
    });
});

createModal('tournament', 'Tournament', `
    <form id="playerForm" class="form" novalidate>
        <p class="font">Select number of players:</p>
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="playerCount" id="4vs4" value="4">
                    <label class="form-check-label font" for="4vs4">4</label>
                </div>
            </div>
            <div class="col-md-6">
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="playerCount" id="8vs8" value="8">
                    <label class="form-check-label font" for="8vs8">8</label>
                </div>
            </div>
        </div>
        <div id="playerAliasInputs" style="display: none;">
                <!-- Player alias inputs will be dynamically added here -->
        </div>
        <button type="submit" id="startTournament" class="submit">Play</button>
        <button type="button" id="randomNamesButton" class="submit">Randomize Names</button>
    </form>`)

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

createModal('logout', 'Log out', `
        <div class="modal-body">
            <p class="ErrorMessage">Are you sure you want to log out?</p>
        </div>
        <div class="modal-footer">
            <button type="button" class="submit" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="submit" onclick="confirmLogout()">Yes, Log out</button>
        </div>`);

insertModal('.about', 'aboutModal.html', 'about', 'About');

createModal('Friends', 'Friends', '<div id="Friends"> <h2 id="friendsList">Friend List</h2> <h2 id="pendingList"> Pending requests </h2> </div>');

createModal('Profile', 'Profile', '<div id="userProfile"></div>');

