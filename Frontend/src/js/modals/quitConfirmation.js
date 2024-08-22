import * as bootstrap from 'bootstrap';

export function initializeConfirmationModal(modalId) {

	const confirmationModalElement = document.getElementById('confirmationModal');
	const confirmationModal = new bootstrap.Modal(confirmationModalElement, {
		keyboard: false,
		backdrop: 'static'
	});

	let isConfirmed = false;

    document.getElementById(modalId).addEventListener('hide.bs.modal', function(event){
        // console.log("in ", modalId, ".hide with isConfirmed:", isConfirmed);
        if (!isConfirmed) {
            // console.log("no confirmation.. preventing default");
            event.preventDefault();
            confirmationModal.show();
        } else {
            isConfirmed = false;
        }
     });

    // Handle confirmation modal buttons
    document.getElementById('cancelClose').addEventListener('click', function () {
        confirmationModal.hide();
    });

    document.getElementById('confirmClose').addEventListener('click', function () {
        isConfirmed = true;
        confirmationModal.hide();
        // console.log("calling modalId.hide() with isConfirmed:", isConfirmed);
        const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
        modal.hide(); // Use Bootstrap's native method to hide the modal
    });
}
