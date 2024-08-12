import * as THREE from 'three';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
//import fontJson from 'three/examples/fonts/droid/droid_sans_regular.typeface.json'; // Adjust path if necessary
import fontJson from '/assets/fonts/teko_light_regular.json'; // Adjust path if necessary
import { degreesToRads } from '../utils.js';
import { vertexShader } from '../shaders/vertexShader.js';
import { scoreBoardShader } from '../shaders/scoreBoardShader.js';
import { WIDTH, HEIGHT } from '../constants.js';
import { convertToRange } from '../utils.js';
import { globalState } from '../globalState.js';

class ScoreBoard {
    constructor(scene) {
        this.scene = scene;
        this.player1Mesh = null;
        this.player2Mesh = null;
        this.goalMesh = null;
        this.gameStartMesh = null;
        this.font = new FontLoader().parse(fontJson);

        // Array to store material instances
        this.materials = [];
    }

    createText(text, size, color, base, speed) {
        const geometry = new TextGeometry(text, {
            font: this.font,
            size: size,
            depth: 3,
            curveSegments: 12,
        });

        // Create a new material instance for each text mesh
        const material = new THREE.ShaderMaterial({
            vertexShader: vertexShader,
            fragmentShader: scoreBoardShader,
            transparent: true,
            depthWrite: false,
            uniforms: {
                color: { value: new THREE.Color(color) },
                iTime: { value: globalState.iTime },
                base: { value: base },
                speed: { value: speed },
            },
        });

        // Store the material instance
        this.materials.push(material);

        const mesh = new THREE.Mesh(geometry, material);

        // Compute the bounding box of the geometry
        geometry.computeBoundingBox();
        const boundingBox = geometry.boundingBox;

        // Calculate the center of the bounding box
        const center = new THREE.Vector3();
        boundingBox.getCenter(center);

        // Reposition the geometry so that its center is at the origin
        geometry.translate(-center.x, -center.y, -center.z);

        return mesh;
    }

    createScoreBoard(player1Text, player2Text) {
        this.clearScores();
        this.player1Mesh = this.createText(player1Text, 70, 0xFFFF00, 1.0, 2.0); // Green for Player 1
        this.player2Mesh = this.createText(player2Text, 70, 0xFF0000, 1.0, 2.0); // Red for Player 2

        // Set positions for player scores

        this.player1Mesh.position.set(0, 140.0, 300.0);
        this.player2Mesh.position.set(0, 60.0, 300.0);

        if (globalState.invertedView === true) {
            this.player1Mesh.rotation.y = THREE.MathUtils.degToRad(180);
            this.player2Mesh.rotation.y = THREE.MathUtils.degToRad(180);
        } else {
            this.player1Mesh.position.z = -300.0;
            this.player2Mesh.position.z = -300.0;
        }
        this.scene.add(this.player1Mesh);
        this.scene.add(this.player2Mesh);
    }

    updateScores(player1Alias, player1Score, player2Alias, player2Score) {
        const player1Text = `${player1Alias} ${player1Score}`;
        const player2Text = `${player2Alias} ${player2Score}`;
        this.createScoreBoard(player1Text, player2Text);
    }

    showGoalText() {
        this.clearScores();
        this.goalMesh = this.createText('GOAL !!!', 100, 0x00FF00, 0.3, 15.0); // green for GOAL text
        this.goalMesh.position.set(0, 90.0, 300.0);
        if (globalState.invertedView === true) {
            this.goalMesh.rotation.y = THREE.MathUtils.degToRad(180);
        } else {
            this.goalMesh.position.z = -300.0;
        }
        this.scene.add(this.goalMesh);
    }

    showGameStartText() {
        this.clearScores();
        this.gameStartMesh = this.createText('GAME START', 80, 0x00FF00, 0.3, 15.0)
        this.gameStartMesh.position.set(0, 90.0, 300.0);
        if (globalState.invertedView === true) {
            this.gameStartMesh.rotation.y = THREE.MathUtils.degToRad(180);
        }
        else {
            this.gameStartMesh.position.z = -300.0
        }
        this.scene.add(this.gameStartMesh);
    }

    showWaitText() {
        this.clearScores();
        this.gameStartMesh = this.createText('Waiting for your opponent..', 50, 0x4455FF, 1.4, 4.0);
        this.gameStartMesh.position.set(0, 90.0, 300.0);
        if (globalState.invertedView === true) {
            this.gameStartMesh.rotation.y = THREE.MathUtils.degToRad(180);
        }
        else {
            this.gameStartMesh.position.z = -300.0
        }
        this.scene.add(this.gameStartMesh);
    }

    
    clearScores() {
        if (this.player1Mesh) {
            this.scene.remove(this.player1Mesh);
            this.player1Mesh.geometry.dispose();
            this.player1Mesh.material.dispose();
            this.player1Mesh = null;
        }
        if (this.player2Mesh) {
            this.scene.remove(this.player2Mesh);
            this.player2Mesh.geometry.dispose();
            this.player2Mesh.material.dispose();
            this.player2Mesh = null;
        }
        if (this.goalMesh) {
            this.scene.remove(this.goalMesh);
            this.goalMesh.geometry.dispose();
            this.goalMesh.material.dispose();
            this.goalMesh = null;
        }
        if (this.gameStartMesh) {
            this.scene.remove(this.gameStartMesh);
            this.gameStartMesh.geometry.dispose();
            this.gameStartMesh.material.dispose();
            this.gameStartMesh = null;
        }
        // Clear the stored materials
        this.materials = [];
    }
}

export default ScoreBoard;