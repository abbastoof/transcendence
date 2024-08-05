import * as THREE from 'three';
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
import fontJson from 'three/examples/fonts/droid/droid_sans_regular.typeface.json'; // Adjust path if necessary

class ScoreBoard {
    constructor(scene) {
        this.scene = scene;
        this.scoreMesh = null;
        this.font = new FontLoader().parse(fontJson);
    }

    createText(text, size, color = 0xFFFFFF) {
        const geometry = new TextGeometry(text, {
            font: this.font,
            size: size,
            depth: 1,
            curveSegments: 12,
        });
        const material = new THREE.MeshPhongMaterial({ color: color });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(-100, 90, -300); // Adjust position as needed
        return mesh;
    }

    createScoreBoard(text) {
        this.scoreMesh = this.createText(text, 30);
        this.scene.add(this.scoreMesh);
    }

    updateScores(player1Score, player2Score) {
        this.clearScores();
        const text = `Player 1: ${player1Score}\nPlayer 2: ${player2Score}`;
        this.createScoreBoard(text);
    }

    showGoalText() {
        this.clearScores();
        console.log("nyt pitäs näyttää maaliteksti")
        this.scoreMesh = this.createText('GOAL!!!', 50, 0xFFFF00);
        this.scene.add(this.scoreMesh);
    }

    clearScores() {
        if (this.scoreMesh) {
            this.scene.remove(this.scoreMesh);
            this.scoreMesh.geometry.dispose();
            this.scoreMesh.material.dispose();
            this.scoreMesh = null;
        }
    }
}

export default ScoreBoard;
