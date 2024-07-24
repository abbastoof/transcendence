import { HEIGHT, WIDTH, LEFT_PADDLE_START, RIGHT_PADDLE_START } from './constants.js';

export const degreesToRads = deg =>(deg * Math.PI) / 180.00;

export function translateCoordinates(data) {
    return {
        player1_position: {
            x: LEFT_PADDLE_START.x,
            y: 0,
            z: data.player1_position.z - HEIGHT / 2
        },
        player2_position: {
            x: RIGHT_PADDLE_START.x,
            y: 0,
            z: data.player2_position.z - HEIGHT / 2
        },
        ball: {
            x: data.ball.x - WIDTH / 2,
            y: data.ball.y,
            z: data.ball.z - HEIGHT / 2
        }
    };
}