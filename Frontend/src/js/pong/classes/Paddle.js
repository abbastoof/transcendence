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
        
        // Edges geometry and material
        this.edgesGeometry = new THREE.EdgesGeometry(this.geometry);
        this.edgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 1.5}); // black color for edges
        this.edgesMesh = new THREE.LineSegments(this.edgesGeometry, this.edgesMaterial);
        this.edgesMesh.position.copy(position);

        this.boundingBox = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
        this.boundingBox.setFromObject(this.mesh);
        
        this.speed = PADDLE_SPEED;
        
    }
    addToScene()
    {
        this.scene.add(this.mesh);
        this.scene.add(this.edgesMesh);
    }
    removeFromScene() {
        // Remove the meshes from the scene
        this.scene.remove(this.mesh);
        this.scene.remove(this.edgesMesh);

        // Dispose of the meshes' geometry
        if (this.mesh.geometry) {
            this.mesh.geometry.dispose();
        }

        if (this.edgesMesh.geometry) {
            this.edgesMesh.geometry.dispose();
        }

        // Dispose of the mesh's material(s)
        if (this.mesh.material) {
            if (Array.isArray(this.mesh.material)) {
                this.mesh.material.forEach(material => material.dispose());
            } else {
                this.mesh.material.dispose();
            }
        }

        if (this.edgesMesh.material) {
            if (Array.isArray(this.edgesMesh.material)) {
                this.edgesMesh.material.forEach(material => material.dispose());
            } else {
                this.edgesMesh.material.dispose();
            }
        }

        // Dispose of textures if any
        this.mesh.traverse(child => {
            if (child.isMesh) {
                if (child.material.map) {
                    child.material.map.dispose();
                }
            }
        });
    }
        
    move(deltaZ){
        this.mesh.position.z += deltaZ;
        this.boundingBox.setFromObject(this.mesh);
        this.edgesMesh.position.copy(this.mesh.position);
    }
    
    updatePosition(position) {
        this.mesh.position.set(position.x, this.mesh.position.y, position.z);
        this.boundingBox.setFromObject(this.mesh);
        this.edgesMesh.position.copy(this.mesh.position);
    }
    intersectsWall(wallBoundingBox)
    {
        return this.boundingBox.intersectsBox(wallBoundingBox);
    }
}

export default Paddle;