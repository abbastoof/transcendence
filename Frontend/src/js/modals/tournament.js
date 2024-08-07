import * as bootstrap from 'bootstrap';
import { startGame, endGame } from '../pong/pong.js';
import GameSession from '../pong/classes/GameSession.js';

document.addEventListener('DOMContentLoaded', function () {
    const playerForm = document.getElementById('playerForm');
    const playerAliasInputs = document.getElementById('playerAliasInputs');
    const modalElement = document.getElementById('tournamentModal');
    const modal = new bootstrap.Modal(modalElement);
    const startTournamentButton = document.getElementById('startTournament');
    const randomNamesButton = document.getElementById('randomNamesButton');
    const pongModal = new bootstrap.Modal(document.getElementById('pongModal')); // Peli modalin määrittely

    const randomNames = [
        "CookieLover", "JarJarBinks", "SillyGoose", "FuzzyWuzzy", 
        "CaptainGiggles", "BumbleBee", "JollyJumper", "WackyWabbit", 
        "SneakySquirrel", "CrazyCat", "FunkyMonkey", "NinjaNoodle", 
        "GiggleGuru", "HappyHippo", "ZanyZebra", "LaughingLion"
    ];

    localStorage.clear();

    let tournamentPlayers = [];
    let round = 1;
    let totalRounds = 0;
    let isFinal = false;
    let isGoing = false;
    let currentGame = 0;
    let seed = Math.floor(Math.random() * 1000 + 1000);


    localStorage.setItem('isFinal',isFinal);

    playerForm.addEventListener('change', function (event) {
        const selectedPlayerCount = playerForm.querySelector('input[name="playerCount"]:checked');

        if (selectedPlayerCount) {
            const numPlayers = parseInt(selectedPlayerCount.value);
            const existingAliases = {};

            // Store current aliases
            for (let i = 1; i <= playerAliasInputs.children.length; i++) {
                const input = playerAliasInputs.querySelector(`input[name="playerAlias${i}"]`);
                if (input) {
                    existingAliases[`playerAlias${i}`] = input.value;
                }
            }

            playerAliasInputs.innerHTML = ''; // Clear previous inputs

            // Create new input fields
            for (let i = 1; i <= numPlayers; i++) {
                const inputGroup = document.createElement('div');
                inputGroup.classList.add('form-group');

                const label = document.createElement('label');
                label.textContent = `Player ${i} Alias:`;
                label.classList.add('labelFont');

                const input = document.createElement('input');
                input.setAttribute('type', 'text');
                input.type = 'text';
                input.setAttribute('name', `playerAlias${i}`);
                input.setAttribute('placeholder', `Player ${i} Alias`);
                input.classList.add('form-control');
                input.required = true;
                input.maxLength = 15;

                // Restore previous value if available
                if (existingAliases[`playerAlias${i}`]) {
                    input.value = existingAliases[`playerAlias${i}`];
                }

                inputGroup.appendChild(label);
                inputGroup.appendChild(input);
                playerAliasInputs.appendChild(inputGroup);
   
            }
            
            randomNamesButton.style.display = 'block';
            startTournamentButton.style.display = 'block';
            playerAliasInputs.style.display = 'block';
        }
    });

    randomNamesButton.addEventListener('click', function () {
        const playerCount = parseInt(document.querySelector('input[name="playerCount"]:checked').value);
        if (isNaN(playerCount) || playerCount <= 0) {
            alert("Valitse pelaajien määrä.");
            return;
        }
        
        const inputs = playerAliasInputs.querySelectorAll('input[type="text"]');
        const shuffledNames = randomNames.sort(() => 0.5 - Math.random()).slice(0, playerCount);
        
        // Tarkistetaan, ettei tule samoja nimiä pelaajille
        const usedNames = new Set();

        inputs.forEach((input, index) => {
            let name = shuffledNames[index];
            while (usedNames.has(name)) {
                name = randomNames[Math.floor(Math.random() * randomNames.length)];
            }
            usedNames.add(name);
            input.value = name;
        });
    });

    playerForm.addEventListener('submit', function (event) {
        
        tournamentPlayers = [];
        event.preventDefault();

        const inputs = playerAliasInputs.querySelectorAll('input');
        inputs.forEach((input, index) => {
            if(input.value.trim() !== '') {
                tournamentPlayers.push({ id: index + 1, name: input.value.trim() });
            }
        });

        if (playerForm.checkValidity()) {
            localStorage.setItem('tournamentPlayers', JSON.stringify(tournamentPlayers));
            localStorage.setItem('remainingPlayers', JSON.stringify(tournamentPlayers));
            localStorage.setItem('winners', JSON.stringify([]));

            totalRounds = Math.log2(tournamentPlayers.length);
            localStorage.setItem('totalRounds', totalRounds);
            round = 1;
            localStorage.setItem('actualRound', round);
            createGamePairs();
            startNextGame();
        } else {
            playerForm.classList.add('was-validated');
        }

        // Simulate sending data to backend (for testing locally)
        console.log('Simulating sending player names to backend:', tournamentPlayers);

        // Reset the form and clear inputs
        playerForm.reset();
        playerAliasInputs.innerHTML = '';
        modal.hide();
    });

    function createGamePairs(){
        let gamePairs = [];
        let remainingPlayers = JSON.parse(localStorage.getItem('remainingPlayers'));

        while (remainingPlayers.length > 1) {
            let player1 = remainingPlayers.splice(Math.floor(Math.random() * remainingPlayers.length), 1)[0];
            let player2 = remainingPlayers.splice(Math.floor(Math.random() * remainingPlayers.length), 1)[0];
            const pairPlayed = { played: false };
            gamePairs.push([
                player1, 
                player2,
                pairPlayed
            ]);
            localStorage.setItem('gamePairs', JSON.stringify(gamePairs));
        }
        localStorage.setItem('remainingPlayers',JSON.stringify([]));
        // debugger;
    }

    function startNextGame() {

        let winners = JSON.parse(localStorage.getItem('winners'));
        let gamePairs = JSON.parse(localStorage.getItem('gamePairs'));
        localStorage.setItem('isGameOver', 'false');
        
        if(!isFinal) {
            for (let i = 0; i < gamePairs.length; i++) {
                if(!gamePairs[i][2].played) {
                    const config = {
                        isRemote: false,
                        playerIds: [gamePairs[i][0].id, gamePairs[i][1].id],
                        gameId: seed + currentGame,
                        isLocalTournament: true
                    };
                    currentGame++;
                    pongModal.show();
                    startGame('pongGameContainer', config, gameResultCallBack);
                    gamePairs[i][2].played = true;
                    localStorage.setItem('gamePairs', JSON.stringify(gamePairs));
                    break;
                }
            }
        } else if(isFinal && winners.length === 2) {
            const config = {
                isRemote: false,
                playerIds: winners,
                gameId: seed + currentGame,
                isLocalTournament: true
            };
            pongModal.show();
            startGame('pongGameContainer', config, gameResultCallBack);
        }

    }

    function gameResultCallBack(data) {

        let winners = JSON.parse(localStorage.getItem('winners'));
        const tournamentPlayers = JSON.parse(localStorage.getItem('tournamentPlayers'));
        let remainingPlayers = JSON.parse(localStorage.getItem('remainingPlayers'));

        if (!winners.includes(data.winner)) {
            let winner = { id: data.winner, name: tournamentPlayers[data.winner - 1].name };
            remainingPlayers.push(winner);
            localStorage.setItem('remainingPlayers', JSON.stringify(remainingPlayers));
            winners.push(data.winner);
        }
        console.log("Winners: ", winners);
        localStorage.setItem('winners', JSON.stringify(winners));

        if (winners.length === tournamentPlayers.length / Math.pow(2, round)) {
            console.log("Turnaus päättynyt. Voittaja on: " + tournamentPlayers[data.winner - 1].name);
        } else if (winners.length === 2) {
            console.log("juuh")
            waitForGameOver(startNextGame); // Finaali
        } else {
            round++;
            localStorage.setItem('actualRound', round);
            // tee tähän tarkistus kun ensimmäinen kierros on päättynyt, sitten luodaan uusi pariryhmä
            // createGamePairs();
            console.log("jooh");
            // sitten aloita uusi kierros uusilla pareilla
            waitForGameOver(startNextGame);
        }

    }
    // callback function should close pong modal, open new modal with result and "continue" button
    function waitForGameOver(callback) {
        const interval = setInterval(() => {
            if (localStorage.getItem('isGameOver') === 'true') {
                clearInterval(interval);
                callback();
            }
        }, 100); // Tarkistaa 100 ms välein
    }

    // Event listener for when the modal is closed
    modalElement.addEventListener('hidden.bs.modal', function () {
        // Reset the form and clear inputs
        playerForm.reset();
        playerAliasInputs.innerHTML = '';
    });
});

