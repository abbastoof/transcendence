import * as THREE from 'three';
import { PADDLE_SPEED, PADDLE_THICKNESS, PADDLE_WIDTH } from '../constants.js';

class Paddle {
    constructor(scene, position, paddleColor) {
        this.scene = scene;
        this.geometry = new THREE.BoxGeometry(PADDLE_THICKNESS, PADDLE_THICKNESS, PADDLE_WIDTH);
        this.material = new THREE.MeshToonMaterial({ color: paddleColor});
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.copy(position);
        this.mesh.receiveShadow = true;
        this.speed = PADDLE_SPEED;
        this.boundingBox = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
        this.boundingBox.setFromObject(this.mesh);
    }
    addToScene()
    {
        this.scene.add(this.mesh);
    }
    updatePosition(position) {
        this.mesh.position.set(position.x, this.mesh.position.y, position.z);
        this.boundingBox.setFromObject(this.mesh);
    }
    intersectsWall(wallBoundingBox)
    {
        return this.boundingBox.intersectsBox(wallBoundingBox);
    }
}
export default Paddle;