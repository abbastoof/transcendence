#from django.test import TestCase

import unittest
import math
import logging


from entities.position import Position
from entities.paddle import Paddle
from entities.player import Player
from entities.ball import Ball
from entities.gamestate import GameState
from game_defaults import *

# Create your tests here.

class TestPosition(unittest.TestCase):
    def setUp(self):
        self.position = Position(14, 21, 45)
    
    def test_initial_position(self):
        self.assertEqual(self.position, Position(14, 21, 45))

    def test_set_position(self):
        self.position = Position(42, 42, 42)
        self.assertEqual(self.position, Position(42, 42, 42))
    
    def test_get_x(self):
        self.assertEqual(self.position.x, 14)

    def test_set_x(self):
        self.position.x = 42
        self.assertEqual(self.position.x, 42)
    
    def test_get_y(self):
        self.assertEqual(self.position.y, 21)
    
    def test_set_y(self):
        self.position.y = 42
        self.assertEqual(self.position.y, 42)

    def test_get_z(self):
        self.assertEqual(self.position.z, 45)

    def test_set_z(self):
        self.position.z = 42
        self.assertEqual(self.position.z, 42)

    def test_as_tuple(self):
        x, y, z = self.position.as_tuple()
        self.assertEqual((x, y, z), (14, 21, 45))
        
class TestPaddle(unittest.TestCase):
    
    def setUp(self):
        self.paddle = Paddle(50)
    
    def test_initial_position(self):
        expected_z = PLAYER_START_Z
        self.assertEqual(self.paddle.position, Position(50, 0, expected_z))#{'x': 50, 'y': 0, 'z': 150})

    def test_move(self):
        old_z = self.paddle.z
        self.paddle.move(5)
        self.assertEqual(self.paddle.position, Position(50, 0, old_z + 5))
    
    def test_width(self):
        self.assertEqual(self.paddle.width, PADDLE_WIDTH)
    
    def test_depth(self):
        self.assertEqual(self.paddle.depth, PADDLE_DEPTH)

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
        old_z = self.player.paddle.z
        self.player.move_paddle(1)
        self.assertEqual(self.player.paddle.z, old_z + 1)

class TestBall(unittest.TestCase):

    def setUp(self):
        self.ball = Ball(BALL_DEFAULT_X, BALL_DEFAULT_Z, BALL_RADIUS, BALL_SPEED, 42)

    def log_ball_before_bounce(self, paddle, ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle):
        logging.info(f"Bouncing from paddle, paddle z: {paddle.position.z} ")
        logging.info(f"Ball pos z: {ball.z}")
        logging.info(f"Ball deltas before bounce: x {ball.delta_x}, z {ball.delta_z}")
        logging.info(f"hitpos variable: {hitpos}")
        logging.info(f"dz factor: {dz_factor}")
        logging.info(f"direction mod: {direction_mod}")
        logging.info(f"adjustment: {adjustment}")
        logging.info(f"Ball direction before bounce: {ball.direction}")
        logging.info(f"Expected angle: {expected_angle}")

    def log_after_bounce(sell, ball):
        logging.info(f"Direction after bounce: {ball.direction}")
        logging.info(f"Deltas after bounce: x {ball.delta_x}, y {ball.delta_z}")

    def calculate_expected_deltas(self, expected_angle):
        radians: float = math.radians(expected_angle)
        expected_delta_x = math.cos(radians) * self.ball.speed
        expected_delta_z = math.sin(radians) * self.ball.speed
        return expected_delta_x, expected_delta_z
    
    def test_initial_position(self):
        self.assertEqual(self.ball.position, Position(200, 0, BALL_DEFAULT_Z))

    def test_initial_speed(self):
        self.assertEqual(self.ball.speed, BALL_SPEED)
    
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

    def test_bounce_from_paddle_middle1(self):
        self.ball.direction = 0
        self.ball.z = 151
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 150
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 183 + hitpos * adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_middle2(self):
        self.ball.direction = 279
        self.ball.z = 149
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 151
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 177 - hitpos * adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_middle3(self):
        self.ball.direction = 110
        self.ball.z = 205
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 200
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor   
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)   
        expected_angle = 3 + hitpos * adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_middle4(self):
        self.ball.direction = 180.5
        self.ball.z = 199
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 200
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor    
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 357 - hitpos * adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_top1(self):
        self.ball.direction = 260
        self.ball.z = 59
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 30
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 10 + adjustment * .5
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_top2(self):
        self.ball.direction = 75
        self.ball.z = 290
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 255
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod

        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor  
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 170 - adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_top3(self):
        self.ball.direction = 179
        self.ball.z = 270
        self.paddle = Paddle(PLAYER1_START_X)
        self.paddle.position.z = 255
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor  
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 10 + adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_top4(self):
        self.ball.direction = 350
        self.ball.z = 98
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 75
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor  
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 170 - adjustment * 0.5
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_bottom1(self):
        self.ball.direction = 260
        self.ball.z = 59
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 80
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 350 - adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_bottom2(self):
        self.ball.direction = 75
        self.ball.z = 230
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 255
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor  
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 190 + adjustment * .5
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_bottom3(self):
        self.ball.direction = 179
        self.ball.z = 130
        self.paddle = Paddle(PLAYER1_START_X)
        self.paddle.position.z = 150
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor  
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 350 - adjustment * 0.5
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})

    def test_bounce_from_paddle_bottom4(self):
        self.ball.direction = 350
        self.ball.z = 48
        self.paddle = Paddle(PLAYER2_START_X)
        self.paddle.position.z = 75
        hitpos = (self.ball.z - self.paddle.position.z) / (self.paddle.width / 2)
        dz_factor = (self.ball.delta_z / self.ball.speed) * 10
        direction_mod = abs((self.ball.direction % 180) - 90)
        if direction_mod > 75:
            direction_mod = 150 - direction_mod
        adjustment = abs(75 - direction_mod) + 5 * abs(hitpos) + dz_factor  
        adjustment = min(adjustment, MAX_BOUNCE_ANGLE_ADJUSTMENT)
        expected_angle = 190 + adjustment
        expected_delta_x, expected_delta_z = self.calculate_expected_deltas(expected_angle)
        self.log_ball_before_bounce(self.paddle, self.ball, hitpos, dz_factor, direction_mod, adjustment, expected_angle)
        self.ball.bounce_from_paddle(self.paddle)
        self.log_after_bounce(self.ball)
        self.assertEqual(self.ball.direction, expected_angle)
        self.assertEqual({self.ball.delta_x, self.ball.delta_z}, {expected_delta_x, expected_delta_z})
    
    def test_collision1(self):
        self.ball.direction = 179
        self.ball.z = 130
        self.ball.x = PLAYER1_START_X + PADDLE_DEPTH + 5
        self.paddle = Paddle(PLAYER1_START_X)
        self.paddle.position.z = 150

        for _ in range(4):
            self.ball.update_position()
            self.assertFalse(self.ball.check_collision(self.paddle))

        self.ball.update_position()
        self.assertTrue(self.ball.check_collision(self.paddle))

    def test_ball_gets_stuck_in_paddle(self):
        self.ball.direction = 330  # ball moving horizontally
        self.ball.z = 150  # same as paddle's z position
        self.ball.x = FIELD_DEPTH - PADDLE_DEPTH - 1
        self.paddle = Paddle(PLAYER2_START_X)
        self.ball.speed = 1  # ball speed is too slow
        self.paddle.position.z = 150
        paddle_z_bottom = self.paddle.z - PADDLE_WIDTH / 2 
        paddle_z_top = paddle_z_bottom + PADDLE_WIDTH
        logging.info(f"Ball gets stuck in paddle test")
        logging.info(f"paddle pos: {self.paddle.position.x}, {self.paddle.position.z} ")
        logging.info(f"Paddle z top: {paddle_z_top}, Paddle z bottom: {paddle_z_bottom}")

        for _ in range(2):  # adjust the range as needed
            logging.info(f"Ball pos: {self.ball.x} {self.ball.z}")
            self.ball.update_position()
            logging.info(f"Ball pos: {self.ball.x} {self.ball.z}")
            if self.ball.check_collision(self.paddle):  # if collision, bounce
                self.ball.bounce_from_paddle(self.paddle)
                self.ball.update_position()  # update position after bounce
                if self.ball.check_collision(self.paddle):  # if collision after bounce
                    logging.info("Ball is stuck in paddle")

    def test_ball_tunneling(self):
        self.ball.direction = 330  # ball moving horizontally
        self.ball.z = 150  # same as paddle's z position
        self.ball.x = FIELD_DEPTH - PADDLE_DEPTH - 1
        self.paddle = Paddle(PLAYER2_START_X)
        self.ball.speed = PADDLE_DEPTH * 2  # ball moves twice the paddle's depth in one step
        self.paddle.position.z = 150
        paddle_z_bottom = self.paddle.z - PADDLE_WIDTH / 2 
        paddle_z_top = paddle_z_bottom + PADDLE_WIDTH
        logging.info(f"Ball tunneling test")
        logging.info(f"paddle pos: {self.paddle.position.x}, {self.paddle.position.z} ")
        logging.info(f"Paddle z top: {paddle_z_top}, Paddle z bottom: {paddle_z_bottom}")

        # Before update, the ball is outside the paddle, so no collision
        self.assertFalse(self.ball.check_collision(self.paddle))

        # Update ball's position
        self.ball.update_position()

        logging.info(f"Ball pos: {self.ball.x} {self.ball.z}")
        # After update, the ball has moved through the paddle, so no collision
        self.assertFalse(self.ball.check_collision(self.paddle))

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

    # def test_run_rally(self):
    #     self.game_state.run_rally()
    #     self.assertEqual(self.game_state.get_player_score(1), 1)



if __name__ == '__main__':
    logging.basicConfig(filename='tests.log', level=logging.INFO)
    unittest.main()

 