### `startGame` Function Overview (Frontend/src/js/pong/pong.js)

#### Purpose:
Initializes and starts a game session in a specified HTML container.

#### Parameters:
- `containerId` (string): ID of the HTML element to host the game.
- `config` (object, optional): Configuration settings for the game.

#### Config Options:
- `isRemote` (boolean): Indicates if the game is remote (default: `false`).
- `playerIds` (array): Array of two player IDs (default: `[]`).
- `gameId` (number): ID of the game (default: `null`).
- `isLocalTournament` (boolean): Indicates if the game is a local tournament (default: `false`).

### Valid Configurations

#### 1. Local Tournament:
- **Description**: Starts a local tournament game with predefined player IDs and game ID.
- **Config**:
  ```javascript
  {
    isLocalTournament: true,
    playerIds: [123, 456],
    gameId: 789,
    isRemote: false
  }
  ```
  ```javascript
  startGame('gameContainer', {
    isLocalTournament: true,
    playerIds: [123, 456],
    gameId: 789,
    isRemote: false
  });
  ```

#### 2. Remote Game:
- **Description**: Starts a remote game using player IDs and gameID's provided by the backend matchmaking. 
- **Note**: The logged-in user must be one of the players. Otherwise the game will not start. Logged in user's id is fetched from `localStorage`
- **Note**: Instead of sending "startgame" message to server like in local games, the client sends a "join game" message to server. Game session can start when both players have joined.
- **Config**:
  ```javascript
  {
    isRemote: true,
    playerIds: [123, 456],
    gameId: 12345,  // Must be a valid number
    isLocalTournament: false
  }
  ```
  ```javascript
  startGame('gameContainer', {
    isRemote: true,
    playerIds: [123, 456],
    gameId: 12345,  // Must be a valid number
    isLocalTournament: false
  });
  ```

#### 3. Standard Local Game:
- **Description**: Starts a local game with random player IDs and game ID.
- **Config**:
  ```javascript
  {
    isRemote: false,
    playerIds: [],
    gameId: null,
    isLocalTournament: false
  }
  ```
  ```javascript
  startGame('gameContainer', {
    isRemote: false,
    playerIds: [],
    gameId: null,
    isLocalTournament: false
  });
  ```

### Key Points:
1. **Validation**: Ensures valid player IDs, game ID, and boolean values.
2. **Local Storage**: Uses user data from `localStorage` for remote games.
3. **Remote Game Restriction**: The logged-in user must be one of the players in a remote game.
4. **HTML Setup**: Creates and appends a canvas to the specified container.
5. **Controls**: Sets up keyboard controls for paddle movement.
6. **Animation**: Starts the game animation loop.

*Remember*:
When you start a game with startGame(), remember to end it with endGame()