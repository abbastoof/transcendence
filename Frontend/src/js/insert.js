function insert(selector, path) {
	const element = document.querySelector(selector);
	if (!element) {
		console.error('Element not found');
		return;
	}

	fetch(path)
		.then(response => response.text())
		.then(html => {
			element.innerHTML = html;
		})
		.catch(error => {
			console.error('Error loading the', error);
		});
}

function insertModal(selector, path, modal) {
	const element = document.querySelector(selector);
	if (!element) {
		console.error('Element not found');
		return;
	}

	fetch(path)
		.then(response => response.text())
		.then(html => {
			createModal(modal, html);
		})
		.catch(error => {
			console.error('Error loading the modal', error);
		});
}