import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { RGBShiftShader } from 'three/addons/shaders/RGBShiftShader.js';
import { DotScreenShader } from 'three/addons/shaders/DotScreenShader.js';
import { GlitchPass } from 'three/addons/postprocessing/GlitchPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import Paddle from './classes/Paddle.js';
import Ball from './classes/Ball.js';
import PlayingField from './classes/PlayingField.js';
import { WIDTH, HEIGHT, LEFT_PADDLE_START, RIGHT_PADDLE_START } from './constants.js';
import { init } from './init.js';
// const light = new THREE.PointLight( 0xffffff, 5.1, 100, 0.5 );
// light.position.set( 0, 0, 0 );
// scene.add( light );
export function startGame() {
    const { renderer, scene, camera, composer } = init();

    var playingField = new PlayingField(scene);
    //var wall1 = new Wall(0);
    var leftPaddle = new Paddle(scene, LEFT_PADDLE_START, 0x00ff00);
    var rightPaddle = new Paddle(scene, RIGHT_PADDLE_START, 0xff0000);
    var ball = new Ball(scene);
    leftPaddle.addToScene();
    rightPaddle.addToScene();
    ball.addToScene();
    playingField.addToScene();

// Variables to hold keyboard state
    var keys = {};
    document.addEventListener('keydown', function(event) {
        keys[event.key] = true;
    });
    document.addEventListener('keyup', function(event) {
        keys[event.key] = false;
    });

    // Update function to move cubes based on keyboard input
    function update() {
        if ((keys['w'] || keys['W']) && !leftPaddle.intersectsWall(playingField.upperWall.boundingBox)) { // Q key
            leftPaddle.moveUp();
        }
        if ((keys['s'] || keys['S']) && !leftPaddle.intersectsWall(playingField.lowerWall.boundingBox)) { // A key
            leftPaddle.moveDown();
        }
        if (keys['ArrowUp'] && !rightPaddle.intersectsWall(playingField.upperWall.boundingBox)) { // Up arrow key
            rightPaddle.moveUp();
        }
        if (keys['ArrowDown'] && !rightPaddle.intersectsWall(playingField.lowerWall.boundingBox)) { // Down arrow key
            rightPaddle.moveDown();
        }
    }

    function checkCollision() {
        if (ball.boundingSphere.intersectsBox(leftPaddle.boundingBox)) {
            ball.bounceFromPaddle(leftPaddle.mesh.position);
            effect2.uniforms[ 'amount' ].value = 0.059;
            return true;
        }
        else if (ball.boundingSphere.intersectsBox(rightPaddle.boundingBox)) {
            ball.bounceFromPaddle(rightPaddle.mesh.position);
            effect2.uniforms[ 'amount' ].value = -0.059;
            return true;
        }
        else if (ball.hitsWall(playingField.lowerWall.boundingBox) || ball.hitsWall(playingField.upperWall.boundingBox)) {
            ball.bounceFromWall();
            return true;
        }
        else
            return false;
    }

    var counter = 0;
    function animate() {
        playingField.shaderMaterial.uniforms.iTime.value = performance.now() / 1000;
    //    playingField.shaderMaterial.uniforms.ballSpeed.value = ball.speed;
        requestAnimationFrame(animate);
        update();
        ball.update();
        // if (checkCollision() === false)
        // {
        //     if (counter % 77 === 0) {
        //         effect2.uniforms[ 'amount' ].value = 0.0055;
        //         // console.log("Counter % 77: " + counter);
        //     }
        //     else if (counter % 101 === 0) {
        //         effect2.uniforms[ 'amount' ].value = 0.019;
        //         //  console.log("Counter % 101: " + counter);
        //         }
        //     else {
        //     effect2.uniforms[ 'amount' ].value = 0.0015;
        //     }
        // }
        counter++;
        camera.lookAt(0,0,0);
        composer.render();
    }
    animate();
}

startGame()