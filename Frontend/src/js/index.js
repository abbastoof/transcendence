import '../scss/styles.scss'
import { createModal } from './createModal.js'
import { insert, insertModal } from './insert.js'
import './pong/pong.js'
import './modals/signup.js';
import './modals/profile.js';
import './modals/login.js';
import './modals/tournament.js';
import './modals/history.js';
import './modals/friends.js';

insert('.headerContainer', 'headerSVG.html');

createModal('gameInfo', 'Game info', `
    <div class="tournamentGameInfo">
        <div class="mb-4 font" id="winner"></div>
        <div class="mb-4 font" id="nextPlayers"></div>
        <button type="button" id="gameInfoButton" class="submit">OK</button>
    </div>`);

createModal('tournament', 'Tournament', `
    <form id="playerForm" class="form">
        <p class="font">Select number of players:</p>
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="playerCount" id="4 players" value="4">
                    <label class="form-check-label font" for="4 players">4</label>
                </div>
            </div>
            <div class="col-md-6">
                <div class="form-check">
                    <input class="form-check-input" type="radio" name="playerCount" id="8 players" value="8">
                    <label class="form-check-label font" for="8 players">8</label>
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
            <input type="email" maxlength="50" class="form-control" id="signUpEmail" placeholder="Enter email"
                required>
        </div>
        <div class="form-group">
            <label class="labelFont" for="signUpUsername">Username</label>
            <input type="text" maxlength="50" class="form-control" id="signUpUsername" placeholder="Enter username"
                required>
        </div>
        <div class="form-group">
            <label class="labelFont" for="signUpPassword">Password</label>
            <input type="password" maxlength="50" class="form-control" id="signUpPassword" placeholder="Enter password"
                required>
        </div>
        <div class="form-group">
            <label class="labelFont" for="signUpRePassword">Re-enter Password</label>
            <input type="password" maxlength="50" class="form-control" id="signUpRePassword"
                placeholder="Re-enter password" required>
        </div>
        <button type="submit" class="submit">Sign up</button>
    </form>
    <form id="verificationForm" style="display: none;">
        <div class="verification">
            <label for="verificationCode" class="labelFont">Verification Code</label>
            <input type="text" maxlength="6" class="form-control" id="verificationCode" placeholder="Enter code" required>
        </div>
        <div class="modal-footer">
            <button type="submit" class="submit">Verify</button>
            <button type="button" id="cancelVerificationButton" class="submit">Cancel</button>
        </div>
    </form>`);

createModal('login', 'Log in', `
    <form id="loginForm" class="form">
        <div class="form-group">
            <label class="labelFont" for="loginUsername">Username</label>
            <input type="text" maxlength="50" class="form-control" id="loginUsername" placeholder="Enter username" required></input>
        </div>
        <div class="form-group">
            <label class="labelFont" for="loginPassword">Password</label>
            <input type="password" maxlength="50" class="form-control" id="loginPassword" placeholder="Enter password" required></input>
       </div>
        <button type="submit" class="submit">Log in</button>
        <div class="row mt-3">
            <p class="font text-center">
                Don't have an account? <a href="#" class="signup-link" data-bs-dismiss="modal" data-bs-toggle="modal" data-bs-target="#signUpModal">Sign up</a>
            </p>
        </div>
    </form>
    <form id="loginVerification" style="display: none;">
        <div class="verification">
            <label for="loginVerificationCode" class="labelFont">Verification Code</label>
            <input type="text" maxlength="6" class="form-control" id="loginVerificationCode" placeholder="Enter code" required>
        </div>
        <div class="modal-footer">
            <button type="submit" class="submit">Verify</button>
            <button type="button" id="cancelLoginVerificationButton" class="submit">Cancel</button>
        </div>
    </form>`);
createModal('logout', 'Log out', `
    <div class="modal-body">
        <p class="ErrorMessage">Are you sure you want to log out?</p>
    </div>
    <div class="modal-footer">
        <button type="button" class="submit" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="submit" onclick="confirmLogout()">Yes, Log out</button>
    </div>`);


createModal('Profile', 'Profile', '<div id="userProfile"></div>');

createModal('Friends', 'Friends', '<div id="Friends"> <h2 id="friendsList">Friend List</h2> <h2 id="pendingList"> Pending requests </h2> </div>');

createModal('History', 'History', '<div id="History"></div>');

insertModal('.about', 'aboutModal.html', 'about', 'About');


