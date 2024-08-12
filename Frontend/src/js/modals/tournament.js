import * as bootstrap from 'bootstrap';
import { startGame, endGame } from '../pong/pong.js';
import GameSession from '../pong/classes/GameSession.js';

document.addEventListener('DOMContentLoaded', async () => {
    const playerForm = document.getElementById('playerForm');
    const playerAliasInputs = document.getElementById('playerAliasInputs');
    const modalElement = document.getElementById('tournamentModal');
    const modal = new bootstrap.Modal(modalElement);
    const startTournamentButton = document.getElementById('startTournament');
    const randomNamesButton = document.getElementById('randomNamesButton');
    const pongModal = new bootstrap.Modal(document.getElementById('pongModal'));
    const gameInfoModal = new bootstrap.Modal(document.getElementById('gameInfoModal'));
    const gameInfoButton = document.getElementById('gameInfoButton');

    const randomNames = [
        "CookieLover", "JarJarBinks", "SillyGoose", "FuzzyWuzzy", 
        "CaptainGiggles", "BumbleBee", "JollyJumper", "WackyWabbit", 
        "SneakySquirrel", "CrazyCat", "FunkyMonkey", "NinjaNoodle", 
        "GiggleGuru", "HappyHippo", "ZanyZebra", "LaughingLion"
    ];

    localStorage.clear();

    let tournamentPlayers = [];
    let currentGame = 0;
    let seed = Math.floor(Math.random() * 1000 + 1000);

    gameInfoButton.addEventListener('click', function () {
        localStorage.setItem('infoScreen', 'false');
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
            modal.hide();

            // initialize tournament variables
            localStorage.setItem('tournamentPlayers', JSON.stringify(tournamentPlayers));
            localStorage.setItem('roundWinners', JSON.stringify([]));

            const numbers = Array.from({ length: tournamentPlayers.length }, (_, index) => index + 1);
            const shuffledNumbers = numbers.sort(() => Math.random() - 0.5);
            localStorage.setItem('remainingIDs', JSON.stringify(shuffledNumbers));

            // start tournament
            tournamentLogic();
        } else {
            playerForm.classList.add('was-validated');
        }
    });

    async function tournamentLogic() {

        let remainingIDs = JSON.parse(localStorage.getItem('remainingIDs'));
        let roundWinners = [];

        while(remainingIDs.length !== 2)
        {
            while(remainingIDs.length !== 0)
            {
                startNextGame();
                while (localStorage.getItem('isGameOver') === 'false')
                    await new Promise(resolve => setTimeout(resolve, 100));

                remainingIDs = JSON.parse(localStorage.getItem('remainingIDs'));
                roundWinners = JSON.parse(localStorage.getItem('roundWinners'));
                let tmpID = roundWinners[roundWinners.length - 1];
                let winnerName = JSON.parse(localStorage.getItem('tournamentPlayers')).find((player) => (player.id === tmpID));

                pongModal.hide();

                document.getElementById('winner').textContent = ("Game Winner: " + winnerName.name);

                localStorage.setItem('infoScreen', 'true');
                gameInfoModal.show();
                while (localStorage.getItem('infoScreen') === 'true')
                    await new Promise(resolve => setTimeout(resolve, 100));
                gameInfoModal.hide();
            }
            remainingIDs = JSON.parse(localStorage.getItem('roundWinners'));
            localStorage.setItem('roundWinners', JSON.stringify([]));
            localStorage.setItem('remainingIDs', JSON.stringify(remainingIDs));
        }
        startNextGame();
        while (localStorage.getItem('isGameOver') === 'false')
            await new Promise(resolve => setTimeout(resolve, 100));
        pongModal.hide();
        roundWinners = JSON.parse(localStorage.getItem('roundWinners'));
        let tmpID = roundWinners[roundWinners.length - 1];
        let winnerName = JSON.parse(localStorage.getItem('tournamentPlayers')).find((player) => (player.id === tmpID));

        pongModal.hide();

        document.getElementById('winner').textContent = ("Tournament Winner: " + winnerName.name);

        localStorage.setItem('infoScreen', 'true');
        gameInfoModal.show();
        while (localStorage.getItem('infoScreen') === 'true')
            await new Promise(resolve => setTimeout(resolve, 100));
        gameInfoModal.hide();
    }

    function startNextGame() {

        let remainingIDs = JSON.parse(localStorage.getItem('remainingIDs'));

        localStorage.setItem('isGameOver', 'false');

        const config = {
            isRemote: false,
            playerIds: [remainingIDs[0], remainingIDs[1]],
            gameId: seed + currentGame,
            isLocalTournament: true
        };

        currentGame++;
        const newRemainingIds = remainingIDs.slice(2);
        localStorage.setItem('remainingIDs', JSON.stringify(newRemainingIds));
        pongModal.show();
        startGame('pongGameContainer', config, gameResultCallBack_testi);
    }

    function gameResultCallBack_testi(data) {
    
        let roundWinners = JSON.parse(localStorage.getItem('roundWinners'));
        roundWinners.push(data.winner);
        localStorage.setItem('roundWinners', JSON.stringify(roundWinners));
    }

    // Event listener for when the modal is closed
    modalElement.addEventListener('hidden.bs.modal', function () {
        // Reset the form and clear inputs
        playerForm.reset();
        playerAliasInputs.innerHTML = '';
    });
});