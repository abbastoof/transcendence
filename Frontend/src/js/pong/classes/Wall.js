import * as THREE from 'three';
import { WIDTH } from '../constants.js';

class Wall { 
    constructor (scene, pos_z) {
        this.geometry = new THREE.BoxGeometry(WIDTH, 10, 5);
        this.material = new THREE.MeshPhongMaterial( { color: 0xFFFFFF});
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, pos_z);
        this.mesh.receiveShadow = true;
        this.boundingBox = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
        this.boundingBox.setFromObject(this.mesh);
        this.scene = scene;
    }
    addToScene() {
        this.scene.add(this.mesh);
    }
}

export default Wall;