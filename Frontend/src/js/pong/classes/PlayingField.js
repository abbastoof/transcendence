import * as THREE from 'three';
import Wall from "./Wall.js";
import { degreesToRads, convertToRange } from '../utils.js';
import { vertexShader } from '../shaders/vertexShader.js';
import { playingFieldShader } from '../shaders/playingFieldShader.js';
import { WIDTH, HEIGHT, randomX, randomY, randomMultiplier } from '../constants.js'; 
import { globalState } from '../globalState.js';

class PlayingField {
    constructor(scene, gameId, player1Id, player2Id) {
        this.planeGeometry = new THREE.PlaneGeometry(WIDTH, HEIGHT);
        globalState.playingFieldMaterial = new THREE.ShaderMaterial({
            vertexShader: vertexShader,
            fragmentShader: playingFieldShader,
            transparent: true,
            depthWrite: false,
            uniforms: {
                iTime: { value: 0.0 },
                iResolution: { value: new THREE.Vector2(WIDTH, HEIGHT) },
                xRand: { value: convertToRange(player1Id, 50, 690) },
                yRand: { value: convertToRange(player2Id, 2124, 5241) },
                multiRand: { value: convertToRange(gameId, 625, 9049) },
                ballDx: { value: 0.5 },
            }
        });
        this.planeMesh = new THREE.Mesh(this.planeGeometry, globalState.playingFieldMaterial);
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
    removeFromScene() {
        this.scene.remove(this.planeMesh);
        this.upperWall.removeFromScene()
        this.lowerWall.removeFromScene()
        if (this.planeGeometry) {
            this.planeGeometry.dispose();
        }
        if (globalState.playingFieldMaterial) {
            globalState.playingFieldMaterial.dispose();
        }
        this.planeMesh.traverse(child => {
            if (child.isMesh) {
                if (child.material.map) {
                    child.material.map.dispose();
                }
            }
        });
    }
}

export default PlayingField;