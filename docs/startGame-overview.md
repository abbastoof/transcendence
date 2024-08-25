### `startGame` Function Overview (Frontend/src/js/pong/pong.js)

#### Purpose:
Initializes and starts a game session in a specified HTML container. Optionally, you can provide a callback function that will be executed after the game ends and the screen has been cleaned up.

#### Parameters:
- `containerId` (string): ID of the HTML element to host the game.
- `config` (object, optional): Configuration settings for the game.
- `onGameEnd` (function, optional): Callback function that is invoked when the game ends and the screen has been cleaned up. This function receives game result data as its parameter.

#### Config Options:
- `isRemote` (boolean): Indicates if the game is remote (default: `false`).
- `playerIds` (array): Array of two player IDs (default: `[]`).
- `gameId` (number): ID of the game (default: `null`).
- `isLocalTournament` (boolean): Indicates if the game is a local tournament (default: `false`).

### Example of Use

#### 1. Local Tournament:
- **Description**: Starts a local tournament game with predefined player IDs and game ID.
  
  ```javascript
  const config = {
    isRemote: false,
    playerIds: [123, 456],
    gameId: 789,
    isLocalTournament: true,
  };
  
  startGame('gameContainer', config, onTournamentGameEnd);
  ```

#### 2. Remote Game:
- **Description**: Starts a remote game using player IDs and game ID provided by the backend matchmaking.
- **Note**: The logged-in user must be one of the players. Otherwise, the game will not start. Logged-in user’s ID is fetched from `localStorage`.
- **Note**: Instead of sending a "start_game" message to the server like in local games, the client sends a "join_game" message. The game session starts when both players have joined.
  
  ```javascript
  const config = {
    isRemote: true,
    playerIds: [123, 456],
    gameId: 12345,
    isLocalTournament: false
  };
  
  startGame('gameContainer', config, onRemoteGameEnd);
  ```

#### 3. Standard Local Game:
- **Description**: Starts a local game with random player IDs and game ID.
  
  ```javascript
  const config = {
    isRemote: false,
    playerIds: [],
    gameId: null,
    isLocalTournament: false
  };
  
  startGame('gameContainer', config, onLocalGameEnd);
  ```

### Example of a Callback Function

The callback function is invoked at the end of the game with `this.onGameEndCallback(data)`, where `data` is a JSON object containing end results and game stats sent by the game server. 

Example JSON data:
```json
{
    "type": "game_over",
    "game_id": 1234,
    "player1_id": 42,
    "player2_id": 808,
    "winner": 42,
    "player1_score": 10,
    "player2_score": 1,
    "player1_hits": 100,
    "player2_hits": 50,
    "longest_rally": 15,
    "game_duration": 300
}
```

### Key Points:
1. **Validation**: Ensures valid player IDs, game ID, and boolean values.
2. **Local Storage**: Uses user data from `localStorage` for remote games.
3. **Remote Game Restriction**: The logged-in user must be one of the players in a remote game.
4. **HTML Setup**: Creates and appends a canvas to the specified container.
5. **Controls**: Sets up keyboard controls for paddle movement.
6. **Animation**: Starts the game animation loop.
7. **Optional Callback**: The `onGameEnd` callback is called after the game ends and the screen has been cleaned up.