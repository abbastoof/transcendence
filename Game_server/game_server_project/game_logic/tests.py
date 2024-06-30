#from django.test import TestCase

import unittest
import math

from game_entities import *
from game_defaults import *

# Create your tests here.

class TestPaddle(unittest.TestCase):
    
    def setUp(self):
        self.paddle = Paddle(50)
    
    def test_initial_position(self):
        self.assertEqual(self.paddle.position, {'x': 50, 'y': 0, 'z': 150})

    def test_move(self):
        self.paddle.move(5)
        self.assertEqual(self.paddle.position, {'x': 50, 'y': 0, 'z': 155})

    def test_attribute_z(self):
        self.paddle.z = 42
        self.assertEqual(self.paddle.z, 42)
    
    def test_attribute_x(self):
        self.paddle.x = 1
        self.assertEqual(self.paddle.x, 1)
    
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
        self.assertEqual(self.ball.position, {'x': 200, 'y': 0, 'z': BALL_DEFAULT_Z})

    def test_initial_speed(self):
        self.assertEqual(self.ball.speed, 5.0)
    
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
        self.ball.position = {'x': 150, 'z': 14}
        self.assertEqual(self.ball.position, {'x': 150, 'y': 0, 'z': 14})

    def test_property_x(self):
        self.ball.x = 14
        self.assertEqual(self.ball.x, 14)

    def test_property_z(self):
        self.ball.z = 130
        self.assertEqual(self.ball.z, 130)

    # def test_update_position(self):
    #     self.ball.update_position()
    #     expected_x = 14 + math.cos(math.radians(self.ball.direction)) * self.ball.speed


if __name__ == '__main__':
    unittest.main()

 