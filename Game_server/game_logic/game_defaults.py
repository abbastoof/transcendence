# default settings for game entities
# values are based on what is in the threejs prototype, but we will find sweet spots later

PADDLE_WIDTH = 100
PADDLE_DEPTH = 16

BALL_RADIUS = 8
BALL_SPEED = 8.0

PADDLE_SPEED = 9.0

GAME_DURATION = 300 # game duration in seconds
                    # need to multiply this with something, set the result as gamestate.time_remaining
                    # and then subtract from it on every loop
                    # or maybe just convert it to a time format that can be shown in the frontend as well

FIELD_DEPTH = 800 # or width if 2d, this is x axis
FIELD_WIDTH = 600 # or height if 2d, this is z axis

PLAYER_START_Z = FIELD_WIDTH / 2
PLAYER1_START_X = 0 - (PADDLE_DEPTH / 2)
PLAYER2_START_X = FIELD_DEPTH + (PADDLE_DEPTH / 2)

BALL_DEFAULT_X = FIELD_DEPTH / 2
BALL_DEFAULT_Z = FIELD_WIDTH / 2
BALL_DEFAULT_DIRECTION = 0 # angle in degrees

MAX_BOUNCE_ANGLE_ADJUSTMENT = 80
