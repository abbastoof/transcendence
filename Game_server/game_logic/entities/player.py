from game_logic.entities.paddle import Paddle

# Player class
# Represents a player in the game
# Properties:
#   - id: the id of the player
#   - paddle: the paddle of the player
#   - score: the score of the player
class Player:
    def __init__(self, id: int, x_position: float):
        self._id: int = id
        self._paddle: Paddle = Paddle(x_position)
        self._score: int = 0
        self._hits: int = 0

    # getter for id
    @property
    def id(self) -> int:
        return self._id
    
    # getter for paddle
    @property
    def paddle(self) -> Paddle:
        return self._paddle

    # getter for score
    @property
    def score(self) -> int:
        return self._score
    
    # setter for score
    @score.setter
    def score(self, new_score: int) -> None:
        self._score = new_score

    # getter for hits
    @property
    def hits(self) -> int:
        return self._hits
    
    # setter for hits
    @hits.setter
    def hits(self, new_hits: int) -> None:
        self._hits = new_hits
    
    # add_hit method
    # increments the player's hits by 1
    def add_hit(self) -> None:
        self._hits += 1
    
    # move_paddle method
    # moves the player's paddle by the given delta z
    def move_paddle(self, delta_z: float) -> None:
        self.paddle.move(delta_z)

    # update_score method
    # increments the player's score by 1
    def update_score(self) -> None:
        self._score += 1
    