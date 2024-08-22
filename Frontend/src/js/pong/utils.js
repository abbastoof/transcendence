import { HEIGHT, WIDTH, LEFT_PADDLE_START, RIGHT_PADDLE_START } from './constants.js';

export const degreesToRads = deg =>(deg * Math.PI) / 180.00;

/**
 * translateCoordinates - Translate the coordinates from the server to the client
 * this function exists because the server and client have different coordinate systems
 * in threejs the origin of the playing field is at the center of the field
 * in the server the origin is at the bottom left of the field
 * @param {object} data - The data from the server
 *
 * @returns {object} - The translated coordinates
 */
export function translateCoordinates(data) {
    return {
        player1Pos: {
            x: LEFT_PADDLE_START.x,
            y: 0,
            z: data.player1Pos.z - HEIGHT / 2
        },
        player2Pos: {
            x: RIGHT_PADDLE_START.x,
            y: 0,
            z: data.player2Pos.z - HEIGHT / 2
        },
        ball: {
            x: data.ballPosition.x - WIDTH / 2,
            y: data.ballPosition.y,
            z: data.ballPosition.z - HEIGHT / 2
        }
    };
}

// The following functions are used to normalize and scale the player and game id's to specific ranges
// to be used as uniforms/variables in the playing field shader
// each game session will have unique animation in the shader based on the player and game id's
// how cool is that?
/**
 * Normalize a number between 0 and 1
 * @param {number} num - The number to normalize
 * @param {number} minNum - The minimum number in the input range
 * @param {number} maxNum - The maximum number in the input range
 * @returns {number} - The normalized value between 0 and 1
 */
function normalize(num, minNum, maxNum) {
    return (num - minNum) / (maxNum - minNum);
}

/**
 * Scale a normalized number to the desired range
 * @param {number} normalized - The normalized number (between 0 and 1)
 * @param {number} minRange - The minimum value of the desired range
 * @param {number} maxRange - The maximum value of the desired range
 * @returns {number} - The scaled value within the desired range
 */
function scaleToRange(normalized, minRange, maxRange) {
    return minRange + normalized * (maxRange - minRange);
}

/**
 * Convert a number to a float within the specified range
 * @param {number} num - The number to convert
 * @param {number} minRange - The minimum value of the desired range
 * @param {number} maxRange - The maximum value of the desired range
 * @param {number} minNum - The minimum number in the input range
 * @param {number} maxNum - The maximum number in the input range
 * @returns {number} - The converted float within the desired range
 */
export function convertToRange(num, minRange, maxRange, minNum = 0, maxNum = 10000) {
    // Normalize the number
    const normalized = normalize(num, minNum, maxNum);
    // Scale to the desired range
    return scaleToRange(normalized, minRange, maxRange);
}
