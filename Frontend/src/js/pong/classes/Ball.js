import * as THREE from 'three';

import { BALL_SIZE } from '../constants.js';

class Ball {
    constructor(scene){
        this.geometry = new THREE.SphereGeometry(BALL_SIZE);
        this.material = new THREE.MeshPhongMaterial( {color: 0xf0f0f0, emissive: 0x00000, specular: 0x111111, shininess: 100} );
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, 0);
        this.scene = scene;
        this.dx = 0;
        this.dy = 0;
    }

    updatePosition(position) {
        this.mesh.position.set(position.x, this.mesh.position.y, position.z);
    }
    
    addToScene(){
        this.scene.add(this.mesh);
    }
    
    removeFromScene() {
        this.scene.remove(this.mesh);
        if (this.geometry) {
            this.geometry.dispose();
        }
        if (this.material) {
            this.material.dispose();
        }
        this.mesh.traverse(child => {
            if (child.isMesh) {
                if (child.material.map) {
                    child.material.map.dispose();
                }
            }});
    }

    predictBallPosition(lastUpdateTime) {
        // Calculate time elapsed since the last update
        const currentTime = performance.now();
        const timeElapsed = (currentTime - lastUpdateTime) / 1000; // Convert to seconds

        // Predict future position based on velocity and time elapsed
        const predictedX = this.mesh.position.x + this.dx * timeElapsed;
        const predictedY = this.mesh.position.y + this.dy * timeElapsed;

        return { x: predictedX, y: predictedY };
    }
}

export default Ball;