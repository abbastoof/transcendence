import * as bootstrap from 'bootstrap';
import { startGame } from '../pong/pong.js';
import GameSession from '../pong/classes/GameSession.js';

document.addEventListener('DOMContentLoaded', async () => {
    const playerForm = document.getElementById('playerForm');
    const playerAliasInputs = document.getElementById('playerAliasInputs');
    const tournamentModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('tournamentModal'));
    const startTournamentButton = document.getElementById('startTournament');
    const randomNamesButton = document.getElementById('randomNamesButton');
    const pongModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('pongModal'));
    const gameInfoModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('gameInfoModal'));
    const gameInfoButton = document.getElementById('gameInfoButton');
    const closeButtons = document.querySelectorAll('button.close');

    const randomNames = [
        "CookieLover", "JarJarBinks", "SillyGoose", "FuzzyWuzzy",
        "CaptainGiggles", "BumbleBee", "JollyJumper", "WackyWabbit",
        "SneakySquirrel", "CrazyCat", "FunkyMonkey", "NinjaNoodle",
        "GiggleGuru", "HappyHippo", "ZanyZebra", "LaughingLion"
    ];

    let tournamentPlayers = [];
    let currentGame = 0;
    let seed = Math.floor(Math.random() * 1000 + 1000);

    randomNamesButton.style.display = 'none';
    startTournamentButton.style.display = 'none';

    if (sessionStorage.getItem('pause') === 'true')
        gameInfoModal.hide();
    if (sessionStorage.getItem('pause2') === 'true') {
        sessionStorage.setItem('remainingIDs', sessionStorage.getItem('remainingIDsTmp'));
        sessionStorage.setItem('roundWinners', sessionStorage.getItem('roundWinnersTmp'));
    }

    // tournamentStages || 0 = reset || 1 = before first game || 2 = all other games except final || 3 = final
    if(parseInt(sessionStorage.getItem('tournamentStages')))
        tournamentLogic();

    function resetTournament() {
        sessionStorage.setItem('isGameOver', 'true');

        randomNamesButton.style.display = 'none';
        startTournamentButton.style.display = 'none';
        playerForm.reset();
        playerAliasInputs.innerHTML = '';

        sessionStorage.setItem('infoScreen', 'false');
        sessionStorage.setItem('tournamentPlayers', JSON.stringify([]));
        sessionStorage.setItem('remainingIDs', JSON.stringify([]));
        sessionStorage.setItem('roundWinners', JSON.stringify([]));
        sessionStorage.setItem('remainingIDsTmp', JSON.stringify([]));
        sessionStorage.setItem('roundWinnersTmp', JSON.stringify([]));

        sessionStorage.setItem('tournamentStages', '0');

        sessionStorage.setItem('pause', 'false');
        sessionStorage.setItem('pause2', 'false');

        gameInfoModal.hide();

    }

    document.getElementById('gameInfoClose').addEventListener('click', function(event){
        resetTournament();
    });

    randomNamesButton.style.display = 'none';
    startTournamentButton.style.display = 'none';

    document.getElementById('tournamentModal').addEventListener('keydown', function(event){
        if (event.key === "Escape") {
            sessionStorage.setItem('gameQuit', 'true');
        }
    });

    document.getElementById('gameInfoModal').addEventListener('keydown', function(event){
        if (event.key === "Escape") {
            sessionStorage.setItem('gameQuit', 'true');
        }
    });

    document.getElementById('tournamentModal').addEventListener('hidden.bs.modal', function(event){
        if (sessionStorage.getItem('gameQuit') === 'true') {
            resetTournament();
        }
    });

    document.getElementById('gameInfoModal').addEventListener('hidden.bs.modal', function(event){
        if (sessionStorage.getItem('gameQuit') === 'true') {
            resetTournament();
        }
    });

    gameInfoButton.addEventListener('click', function () {
        sessionStorage.setItem('infoScreen', 'false');
    })

    playerForm.addEventListener('change', function () {
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

            // Clear previous inputs
            playerAliasInputs.innerHTML = '';

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
            alert("Choose player amount!");
            return;
        }

        const inputs = playerAliasInputs.querySelectorAll('input[type="text"]');
        const shuffledNames = randomNames.sort(() => 0.5 - Math.random()).slice(0, playerCount);

        // Check for identical names
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

    playerForm.addEventListener('submit', async (event) => {

        event.preventDefault();

        if (playerForm.checkValidity()) {
            tournamentPlayers = [];
            const inputs = playerAliasInputs.querySelectorAll('input');
            inputs.forEach((input, index) => {
                if(input.value.trim() !== '')
                    tournamentPlayers.push({ id: index + 1, name: input.value.trim() });
            });

            // Reset the form and clear inputs
            playerForm.reset();
            playerAliasInputs.innerHTML = '';
            sessionStorage.setItem('roundWinners', JSON.stringify([]));
            tournamentModal.hide();

            // initialize tournament variables
            sessionStorage.setItem('tournamentPlayers', JSON.stringify(tournamentPlayers));

            const numbers = Array.from({ length: tournamentPlayers.length }, (_, index) => index + 1);
            const shuffledNumbers = numbers.sort(() => Math.random() - 0.5);
            sessionStorage.setItem('remainingIDs', JSON.stringify(shuffledNumbers));

            // start tournament
            sessionStorage.setItem('tournamentStages', '1');
            sessionStorage.setItem('gameQuit', 'false');
            tournamentLogic();
        } else {
            playerForm.classList.add('was-validated');
        }
    });

    async function tournamentLogic() {

        let remainingIDs = JSON.parse(sessionStorage.getItem('remainingIDs'));

        let roundWinners = [];
        let winnerName = [];
        let tmpPlayerOne = [];
        let tmpPlayerTwo = [];

        if (sessionStorage.getItem('gameQuit') === 'true') {
            resetTournament();
            return ;
        }

        if(parseInt(sessionStorage.getItem('tournamentStages')) === 1) {
            tmpPlayerOne = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === remainingIDs[0]));
            tmpPlayerTwo = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === remainingIDs[1]));

            document.getElementById('winner').textContent = [];
            document.getElementById('nextPlayers').textContent = ("Next Players: " + tmpPlayerOne.name + " and " + tmpPlayerTwo.name);

            sessionStorage.setItem('infoScreen', 'true');
            gameInfoModal.show();
            while (sessionStorage.getItem('infoScreen') === 'true')
                await new Promise(resolve => setTimeout(resolve, 100));

            gameInfoModal.hide();

            sessionStorage.setItem('remainingIDsTmp', sessionStorage.getItem('remainingIDs'));
            sessionStorage.setItem('roundWinnersTmp', sessionStorage.getItem('roundWinners'));

            sessionStorage.setItem('pause2', 'true');
            startNextGame();
            while (sessionStorage.getItem('isGameOver') === 'false')
                await new Promise(resolve => setTimeout(resolve, 100));
            sessionStorage.setItem('pause2', 'false');
            sessionStorage.setItem('tournamentStages', '2');
        }

        if(parseInt(sessionStorage.getItem('tournamentStages')) === 2) {
            while(1)
            {
                if (sessionStorage.getItem('gameQuit') === 'true') {
                    resetTournament();
                    return ;
                }
                remainingIDs = JSON.parse(sessionStorage.getItem('remainingIDs'));
                roundWinners = JSON.parse(sessionStorage.getItem('roundWinners'));

                if(remainingIDs.length === 0 && roundWinners.length === 1) {
                    break ;
                }

                if(roundWinners.length === 0)
                    winnerName = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === remainingIDs[remainingIDs.length - 1]));
                else
                    winnerName = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === roundWinners[roundWinners.length - 1]));

                if(remainingIDs.length !== 0) {
                    tmpPlayerOne = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === remainingIDs[0]));
                    tmpPlayerTwo = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === remainingIDs[1]));
                }
                else {
                    tmpPlayerOne = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === roundWinners[0]));
                    tmpPlayerTwo = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === roundWinners[1]));
                }

                if (winnerName) {
                    document.getElementById('winner').textContent = ("Last game winner: " + winnerName.name);
                    document.getElementById('nextPlayers').textContent = ("Next Players: " + tmpPlayerOne.name + " and " + tmpPlayerTwo.name);
                }

                sessionStorage.setItem('infoScreen', 'true');
                gameInfoModal.show();
                sessionStorage.setItem('pause', 'true');
                while (sessionStorage.getItem('infoScreen') === 'true')
                    await new Promise(resolve => setTimeout(resolve, 100));
                sessionStorage.setItem('pause', 'false');
                gameInfoModal.hide();

                if(remainingIDs.length === 0 && roundWinners.length !== 0) {
                    remainingIDs = JSON.parse(sessionStorage.getItem('roundWinners'));
                    sessionStorage.setItem('roundWinners', JSON.stringify([]));
                    sessionStorage.setItem('remainingIDs', JSON.stringify(remainingIDs));
                }

                sessionStorage.setItem('remainingIDsTmp', sessionStorage.getItem('remainingIDs'));
                sessionStorage.setItem('roundWinnersTmp', sessionStorage.getItem('roundWinners'));

                sessionStorage.setItem('pause2', 'true');
                startNextGame();
                while (sessionStorage.getItem('isGameOver') === 'false')
                    await new Promise(resolve => setTimeout(resolve, 100));
                sessionStorage.setItem('pause2', 'false');
            }
            sessionStorage.setItem('tournamentStages', '3');
        }

        if(parseInt(sessionStorage.getItem('tournamentStages'))) {
            roundWinners = JSON.parse(sessionStorage.getItem('roundWinners'));
            winnerName = JSON.parse(sessionStorage.getItem('tournamentPlayers')).find((player) => (player.id === roundWinners[roundWinners.length - 1]));

            document.getElementById('winner').textContent = ("Tournament Winner: " + winnerName.name);
            document.getElementById('nextPlayers').textContent = [];

            sessionStorage.setItem('infoScreen', 'true');
            gameInfoModal.show();
            while (sessionStorage.getItem('infoScreen') === 'true')
                await new Promise(resolve => setTimeout(resolve, 100));
            gameInfoModal.hide();
            resetTournament();
        }
    }

    function startNextGame() {

        let remainingIDs = JSON.parse(sessionStorage.getItem('remainingIDs'));
        let players = JSON.parse(sessionStorage.getItem('tournamentPlayers'));

        if(remainingIDs.length === 0) { return ; }

        sessionStorage.setItem('isGameOver', 'false');

        const config = {
            isRemote: false,
            playerIds: [remainingIDs[0], remainingIDs[1]],
            gameId: seed + currentGame,
            isLocalTournament: true,
            player1Alias: players[remainingIDs[0] - 1].name,
            player2Alias: players[remainingIDs[1] - 1].name
        };

        currentGame++;
        const newRemainingIds = remainingIDs.slice(2);
        sessionStorage.setItem('remainingIDs', JSON.stringify(newRemainingIds));

        startGame('pongGameContainer', config, gameResultCallBack);
    }

    function gameResultCallBack(data) {
        if (data.winner) {
            let roundWinners = JSON.parse(sessionStorage.getItem('roundWinners'));
            roundWinners.push(data.winner);
            sessionStorage.setItem('roundWinners', JSON.stringify(roundWinners));
        }
        else {
            console.error('Game result missing winner:', data);
            resetTournament();
        }
    }
});
