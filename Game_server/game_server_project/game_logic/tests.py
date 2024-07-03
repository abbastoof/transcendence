#from django.test import TestCase

import unittest
import math

from game_entities import *
from game_defaults import *

# Create your tests here.

class TestPosition(unittest.TestCase):
    def setUp(self):
        self.position = Position(14, 21, 45)
    
    def test_initial_position(self):
        self.assertEqual(self.position, Position(14, 21, 45))
        
class TestPaddle(unittest.TestCase):
    
    def setUp(self):
        self.paddle = Paddle(50)
    
    def test_initial_position(self):
        self.assertEqual(self.paddle.position, Position(50, 0, 150))#{'x': 50, 'y': 0, 'z': 150})

    def test_move(self):
        self.paddle.move(5)
        self.assertEqual(self.paddle.position, Position(50, 0, 155))
    
    def test_width(self):
        self.assertEqual(self.paddle.width, 100)
    
    def test_depth(self):
        self.assertEqual(self.paddle.depth, 16)

class TestPlayer(unittest.TestCase):
    
    def setUp(self):
        self.player = Player(1, 50)

    def test_score(self):
        self.player.score = 42
        self.assertEqual(self.player.score, 42)
    
    def test_update_score(self):
        self.player.update_score()
        self.assertEqual(self.player.score, 1)
    
    def test_id(self):
        self.assertEqual(self.player.id, 1)

    def test_move_paddle(self):
        self.player.move_paddle(1)
        self.assertEqual(self.player.paddle.z, 151)

class TestBall(unittest.TestCase):

    def setUp(self):
        self.ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, 42)

    def test_initial_position(self):
        self.assertEqual(self.ball.position, Position(200, 0, BALL_DEFAULT_Z))

    def test_initial_speed(self):
        self.assertEqual(self.ball.speed, 0.5)
    
    def test_initial_direction(self):
        self.assertEqual(self.ball.direction, 42)

    def test_initial_radius(self):
        self.assertEqual(self.ball.radius, 6)

    def test_speed(self):
        self.ball.speed = 4.2
        self.assertEqual(self.ball.speed, 4.2)
    
    def test_direction(self):
        self.ball.direction = 90.1
        self.assertEqual(self.ball.direction, 90.1)
    
    def test_radius(self):
        self.ball.radius = 4
        self.assertEqual(self.ball.radius, 4)

    def test_set_position(self):
        self.ball.position = (105,4,14)
        self.assertEqual(self.ball.position, Position(105,4,14))

    def test_property_x(self):
        self.ball.x = 14
        self.assertEqual(self.ball.x, 14)

    def test_property_z(self):
        self.ball.z = 130
        self.assertEqual(self.ball.z, 130)

    def test_speed_up(self):
        expected_speed = self.ball.speed + 2
        self.ball.speed_up(2)
        self.assertEqual(self.ball.speed, expected_speed)

    def test_update_position(self):
        expected_x = self.ball.x + math.cos(math.radians(self.ball.direction)) * self.ball.speed
        expected_z = self.ball.z + math.sin(math.radians(self.ball.direction)) * self.ball.speed
        self.ball.update_position()
        self.assertEqual(self.ball.position, Position(expected_x, 0,expected_z))

    def test_bounce_from_wall(self):
        expected_direction = (360 - self.ball.direction) % 360
        self.ball.bounce_from_wall()
        self.assertEqual(self.ball.direction, expected_direction)

class TestGameState(unittest.TestCase):
    
    def setUp(self):
        player1 = Player(1, 5)
        player2 = Player(2, 395)
        ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, 42)
        self.game_state = GameState(42, player1, player2, ball)

    def test_game_id(self):
        self.assertEqual(self.game_state.game_id, 42)
    
    def test_player1_id(self):
        self.assertEqual(self.game_state.player1.id, 1)
    
    def test_player2_id(self):
        self.assertEqual(self.game_state.player2.id, 2)

    def test_ball_x(self):
        self.assertEqual(self.game_state.ball.x, 200)

    def test_ball_z(self):
        self.assertEqual(self.game_state.ball.z, 150)

    def test_player1_score(self):
        self.assertEqual(self.game_state.get_player_score(1), 0)
    
    def test_update_player1_score(self):
        self.game_state.update_player_score(1)
        self.assertEqual(self.game_state.get_player_score(1), 1)

    def test_player2_score(self):
        self.assertEqual(self.game_state.get_player_score(2), 0)
    
    def test_update_player2_score(self):
        self.game_state.update_player_score(2)
        self.assertEqual(self.game_state.get_player_score(2), 1)

    def test_get_score_wrong_id(self):
        with self.assertRaises(ValueError) as context:
            self.game_state.get_player_score(42)
        self.assertEqual(str(context.exception), "Invalid player ID")
    
    def test_get_score_wrong_id(self):
        with self.assertRaises(ValueError) as context:
            self.game_state.get_player_score(42)
        self.assertEqual(str(context.exception), "Invalid player ID")
    
    def test_update_score_wrong_id(self):
        with self.assertRaises(ValueError) as context:
            self.game_state.update_player_score(123)
        self.assertEqual(str(context.exception), "Invalid player ID")

    def test_update_game_state(self):
        expected_x = self.game_state.ball.x + math.cos(math.radians(self.game_state.ball.direction)) * self.game_state.ball.speed
        expected_z = self.game_state.ball.z + math.sin(math.radians(self.game_state.ball.direction)) * self.game_state.ball.speed
        self.game_state.update_game_state()
        self.assertEqual(self.game_state.ball.position, Position(expected_x, 0,expected_z))

    def test_goal_scoring(self):
        self.game_state.ball.x = 0
        self.game_state.ball.direction = 180
        self.game_state.update_game_state()
        self.assertEqual(self.game_state.get_player_score(2), 1)

    def test_run_rally(self):
        self.game_state.run_rally()
        self.assertEqual(self.game_state.get_player_score(1), 1)



if __name__ == '__main__':
    unittest.main()

 