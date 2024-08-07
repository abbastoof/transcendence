import * as THREE from 'three';
import { BALL_SIZE } from '../constants.js';

class Ball {
    constructor(scene){
        this.geometry = new THREE.SphereGeometry(BALL_SIZE);
        this.material = new THREE.MeshPhongMaterial( {color: 0xF0F0F0, emissive: 0x00000, specular: 0x111111, shininess: 100} );
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, 0);
        this.scene = scene// console.log(this.direction);
        this.dx = 0;
        this.dy = 0;
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