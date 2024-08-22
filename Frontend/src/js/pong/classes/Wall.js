import * as THREE from 'three';
import { WIDTH } from '../constants.js';

class Wall { 
    constructor (scene, pos_z) {
        this.geometry = new THREE.BoxGeometry(WIDTH, 10, 5);
        this.material = new THREE.MeshPhongMaterial( { color: 0xFFFFFF});
        this.mesh = new THREE.Mesh(this.geometry, this.material);
        this.mesh.position.set(0, 0, pos_z);
        this.mesh.receiveShadow = true;
                this.edgesGeometry = new THREE.EdgesGeometry(this.geometry);
        this.edgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 1.5}); // black color for edges
        this.edgesMesh = new THREE.LineSegments(this.edgesGeometry, this.edgesMaterial);
        this.edgesMesh.position.copy(this.mesh.position); 
        this.boundingBox = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
        this.boundingBox.setFromObject(this.mesh);
        this.scene = scene;
    }
    addToScene() {
        this.scene.add(this.mesh);
        this.scene.add(this.edgesMesh);
    }
    removeFromScene() {
        this.scene.remove(this.mesh);
        this.scene.remove(this.edgesMesh);
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
            }
        });
    }
}

export default Wall;