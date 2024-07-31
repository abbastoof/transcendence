## Game Server README

### Overview

This is the game server for the Mighty Pong Contest. Developed with Python and Socket.IO, the server supports real-time communication between clients and manages game sessions, player interactions, and game state updates.

### Key Features
- **Real-time Gameplay:** WebSocket-based communication for live updates.
- **Game Management:** Handles player sessions, game state management, and game completion.
- **Custom Logging:** Configurable logging to track and debug server activities.

### How to Start a Game

To start a game session, follow these instructions:

1. **Connect to the Server**
   - Connect your client to the server using Socket.IO at `http://game-server:8010/game-server/socket.io`.

2. **Prepare Game Initialization Data**
   - Create an object with the following details:
     - `game_id`: A unique identifier for the game session.
     - `player1_id`: A unique identifier for Player 1.
     - `player2_id`: A unique identifier for Player 2.
     - `is_remote`: Set to `true` for remote games or `false` for local games.

   Example:
   ```javascript
   const gameData = {
     game_id: 'unique_game_id_123',
     player1_id: 'player1_unique_id',
     player2_id: 'player2_unique_id',
     is_remote: false // or true for remote games
   };
   ```

3. **Emit the `start_game` Event**
   - Send the game initialization data to the server to start the game session.
   
   ```javascript
   socket.emit('start_game', gameData, (response) => {
     if (response.error) {
       console.error('Error starting game:', response.message);
     } else {
       console.log('Game started successfully:', response);
     }
   });
   ```

4. **Handle Game Events**
   - Implement event handlers to manage game state updates and end-of-game notifications.

   Example:
   ```javascript
   socket.on('send_game_state', (gameState) => {
     console.log('Game state update:', gameState);
     // Update the frontend with gameState data
   });

   socket.on('game_over', (data) => {
     console.log('Game Over! Winner:', data.winner);
     // Display game over screen or handle end-of-game logic
   });
   ```

### Development Setup

1. **Clone the Repository**
   - Clone the project repository to your local development environment.

2. **Install Dependencies**
   - Install the required Python packages using pip.
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**
   - Start the server using Uvicorn.
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8010 --log-level info
   ```

4. **Build and run the app**
  ```bash
  make
  ```
  
### TODO: Remote Play Integration

The backend is working on matchmaking feature which is coming soon, in the meantime remote play needs to be fully integrated, and handling the ending of the game as well.
Upcoming tasks involve:
- **Game Session Establishment:** Finalize how remote game sessions are set up and managed.
- **Player Matching:** Ensure the system pairs players and starts the game once both are connected and ready.
- **End of the game:** Stats/results are currently sent to frontend, but should they be also sent to game-history service?