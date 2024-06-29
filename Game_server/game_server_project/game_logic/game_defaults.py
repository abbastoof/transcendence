# default settings for game entities
# values are based on what is in the threejs prototype, but we will find sweet spots later

PADDLE_WIDTH = 100
PADDLE_DEPTH = 16

BALL_RADIUS = 6
BALL_SPEED = 5.0

GAME_DURATION = 300 #seconds

FIELD_DEPTH = 400 # or width if 2d, this is x axis
FIELD_WIDTH = 300 # or height if 2d, this is z axis

PLAYER_START_Z = FIELD_WIDTH / 2
PLAYER1_START_X = 0 + PADDLE_DEPTH
PLAYER2_START_X = FIELD_DEPTH - PADDLE_DEPTH

BALL_DEFAULT_X = FIELD_DEPTH / 2
BALL_DEFAULT_Z = FIELD_WIDTH / 2

