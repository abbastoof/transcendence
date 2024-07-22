import * as THREE from 'three';
import Wall from "./Wall.js";
import { degreesToRads } from '../utils.js';
import { vertexShader } from '../shaders/vertexShader.js';
import { fragmentShader } from '../shaders/fragmentShader.js';
import { WIDTH, HEIGHT, randomX, randomY, randomMultiplier } from '../constants.js'; 

class PlayingField {
    constructor(scene) {
        this.planeGeometry = new THREE.PlaneGeometry(WIDTH, HEIGHT);
        this.shaderMaterial = new THREE.ShaderMaterial({
            vertexShader: vertexShader,
            fragmentShader: fragmentShader,
            transparent: true,
            depthWrite: false,
            uniforms: {
                iTime: { value: 0.0 },
                iResolution: { value: new THREE.Vector2(WIDTH, HEIGHT) },
                xRand: { value: randomX },
                yRand: { value: randomY },
                multiRand: { value: randomMultiplier }
            }
        });
        //this.planeMaterial = new THREE.MeshToonMaterial({ color: 0x606060 });
        this.planeMesh = new THREE.Mesh(this.planeGeometry, this.shaderMaterial);
        this.planeMesh.rotateX(degreesToRads(-90));
        this.planeMesh.position.set(0, -5, 0);
        this.scene = scene;
        this.lowerWall = new Wall(this.scene, HEIGHT / 2);
        this.upperWall = new Wall(this.scene, HEIGHT / -2);
    }
    addToScene() {
        this.scene.add(this.planeMesh);
        this.upperWall.addToScene()
        this.lowerWall.addToScene()
    }
}

export default PlayingField;