import { createModal } from './createModal.js';

export function insert(selector, path) {
	const element = document.querySelector(selector);
	if (!element) {
		console.error('Element not found');
		return;
	}

	fetch('../html/' + path) // Prepend "html/" to the path variable
		.then(response => response.text())
		.then(html => {
			element.innerHTML = html;
		})
		.catch(error => {
			console.error('Error loading the', error);
		});
}

export function insertModal(selector, path, modal, title) {
	const element = document.querySelector(selector);
	if (!element) {
		console.error('Element not found');
		return;
	}

	fetch('../html/' + path) // Prepend "html/" to the path variable
		.then(response => response.text())
		.then(html => {
			createModal(modal, title, html);
		})
		.catch(error => {
			console.error('Error loading the modal', error);
		});
}