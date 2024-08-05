import * as THREE from 'three';
import { BALL_SIZE } from '../constants.js';

class Ball {
    constructor(scene){
        this.geometry = new THREE.SphereGeometry(BALL_SIZE);
        this.material = new THREE.MeshToonMaterial( {color: 0xffffff });
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, 0);
        this.scene = scene// console.log(this.direction);
    }
    updatePosition(position) {
        this.mesh.position.set(position.x, this.mesh.position.y, position.z);
        // Update bounding sphere position if needed
    }
    addToScene(){
        this.scene.add(this.mesh);
    }
}

export default Ball;