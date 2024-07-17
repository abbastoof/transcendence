import * as THREE from 'three';
import { randFloat } from 'three/src/math/MathUtils';

export const randomX = randFloat(50.0, 690.0);
export const randomY = randFloat(2124.0, 5291.0);
export const randomMultiplier = randFloat(625.0, 90909.0);
export const WIDTH = 800;
export const HEIGHT = 600;
export const BALL_SIZE_RATIO = 0.01;
export const BALL_SIZE = Math.min(WIDTH, HEIGHT) * BALL_SIZE_RATIO;
export const PADDLE_SPEED = 5.0;
export const BALL_SPEED = 5.0;
export const PADDLE_THICKNESS = WIDTH / 50;
export const PADDLE_WIDTH = WIDTH / 8;
export const LEFT_PADDLE_START = new THREE.Vector3(-(WIDTH / 2) + 8, 0, 0);
export const RIGHT_PADDLE_START = new THREE.Vector3((WIDTH / 2) - 8, 0, 0);
