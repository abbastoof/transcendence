import * as bootstrap from 'bootstrap';

/**
 * initialize a confirmation modal that will be shown before closing another modal.
 * The confirmation modal will be shown when the modal with the given modalId is about to be hidden.
 * @param {string} modalId - The id of the modal that will be hidden
 * @param {string} title - The title of the confirmation modal
 * @param {string} message - The message of the confirmation modal
 * @returns {function} bypassConfirmationModal - A function that can be called to bypass the confirmation modal and hide the modal with the given modalId
*/
export function initializeConfirmationModal(modalId, title, message) {

	const confirmationModalElement = document.getElementById('confirmationModal');
	const confirmationModal = new bootstrap.Modal(confirmationModalElement, {
		keyboard: false,
		backdrop: 'static'
	});

	let isConfirmed = false;
	let bypassConfirmation = false;

    document.getElementById(modalId).addEventListener('hide.bs.modal', function(event){
        if (!isConfirmed && !bypassConfirmation) {
            event.preventDefault();
			document.getElementById('confirmationModalTitle').innerText = title;
            document.getElementById('confirmationModalMessage').innerText = message;
            confirmationModal.show();
        }
    });

    // Handle confirmation modal buttons
    document.getElementById('cancelClose').addEventListener('click', function () {
        confirmationModal.hide();
    });

    document.getElementById('confirmClose').addEventListener('click', function () {
        isConfirmed = true;
        confirmationModal.hide();
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        modal.hide(); // Use Bootstrap's native method to hide the modal
        sessionStorage.setItem("gameQuit", "true");
    });

	// function to bypass the confirmation modal
	return function bypassConfirmationModal() {
		bypassConfirmation = true;
		const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
		modal.hide();
	};
}
