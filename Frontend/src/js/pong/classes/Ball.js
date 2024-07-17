import * as THREE from 'three';
import { BALL_SIZE, BALL_SPEED, PADDLE_WIDTH } from '../constants.js';
import { degreesToRads } from '../utils.js';

class Ball {
    constructor(scene){
        this.geometry = new THREE.SphereGeometry(BALL_SIZE);
        this.material = new THREE.MeshToonMaterial( {color: 0xffffff });
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, 0);
        this.direction = 0;
        // console.log(this.direction);
        this.speed = BALL_SPEED;
        this.boundingSphere = new THREE.Sphere(this.mesh.position, BALL_SIZE);
        this.scene = scene
    }
    update() {
        let radians = degreesToRads(this.direction);
        this.mesh.position.x = this.mesh.position.x + Math.cos(radians) * this.speed;
        this.mesh.position.z = this.mesh.position.z + Math.sin(radians) * this.speed;
    }
    hitsWall(wallBoundingBox) {
        return this.boundingSphere.intersectsBox(wallBoundingBox);
    }
    bounceFromPaddle(paddlePos) {
        //this.direction = (360 - this.direction) % 360;
        // console.log(this.direction);
        let hitPosNormalized = (paddlePos.z - this.mesh.position.z) / (PADDLE_WIDTH / 2);
        // console.log("Paddle pos: " + paddlePos.x + " " + paddlePos.z + ", ball pos: " + this.mesh.position.x + " " + this.mesh.position.z)
        // console.log("hitPosNormalized: " + hitPosNormalized);
        if (hitPosNormalized >= 1.0) {
            hitPosNormalized = .9;}
        else if (hitPosNormalized <= -1.0) {
            hitPosNormalized = -.9;
        }
        // console.log("hitPosNormalized: " + hitPosNormalized);

        let directionChange = hitPosNormalized * 85;
        if (paddlePos.x < 0)
            directionChange *= -1;
        // console.log("directionChange: " + directionChange + " degrees")
        this.direction = (180 - this.direction + directionChange) % 360;
        // console.log("new direction: " + this.direction + " degrees")
        this.speed += 0.02 + Math.abs(hitPosNormalized); 
    }
    bounceFromWall() {
        this.direction = (360 - this.direction) % 360; // Reflect the direction
                // console.log(this.direction);
    }
    addToScene(){
        this.scene.add(this.mesh);
    }
};

export default Ball;