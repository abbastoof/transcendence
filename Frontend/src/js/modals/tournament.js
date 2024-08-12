import * as bootstrap from 'bootstrap';

document.addEventListener('DOMContentLoaded', function () {
    const modalElement = document.getElementById('tournamentModal');
    const modal = new bootstrap.Modal(modalElement, {
        backdrop: 'static', // prevent closing on backdrop click
        keyboard: true, // allow closing with ESC currently only works after selecing a player count or pressing tab once
    });
    const playerForm = document.getElementById('playerForm');
    const playerAliasInputs = document.getElementById('playerAliasInputs');

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
                input.setAttribute('name', `playerAlias${i}`);
                input.setAttribute('placeholder', `Player ${i} Alias`);
                input.classList.add('form-control');
                input.required = true;

                // Restore previous value if available
                if (existingAliases[`playerAlias${i}`]) {
                    input.value = existingAliases[`playerAlias${i}`];
                }

                inputGroup.appendChild(label);
                inputGroup.appendChild(input);
                playerAliasInputs.appendChild(inputGroup);
            }

            playerAliasInputs.style.display = 'block';
        }
    });

    playerForm.addEventListener('submit', function (event) {
        event.preventDefault();

        // Collect player aliases
        const formData = new FormData(playerForm);
        const playerNames = [];
        for (let pair of formData.entries()) {
            if (pair[0].startsWith('playerAlias')) {
                playerNames.push(pair[1]);
            }
        }

        // Simulate sending data to backend (for testing locally)
        console.log('Simulating sending player names to backend:', playerNames);

/*
        // Send player names to the server
        fetch('https://example.com/api/save-player-names', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Add any headers needed, like authorization headers
            },
            body: JSON.stringify({ playerNames: playerNames }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Handle success response from server if needed
            console.log('Player names saved successfully:', data);
            // Reset the form and clear inputs
            playerForm.reset();
            playerAliasInputs.innerHTML = '';
            modal.hide();
        })
        .catch(error => {
            // Handle error
            console.error('Error saving player names:', error);
            // Optionally, inform the user about the error
        });
*/

        // Reset the form and clear inputs
        playerForm.reset();
        playerAliasInputs.innerHTML = '';
        modal.hide();
    });

    // Event listener for when the modal is closed
    modalElement.addEventListener('hidden.bs.modal', function () {
        // Reset the form and clear inputs
        playerForm.reset();
        playerAliasInputs.innerHTML = '';
    });
});

