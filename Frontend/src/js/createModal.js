function createModal(modalId, content) {
    const modalHTML = `
    <div class="modal fade" id="${modalId}Modal"  role="dialog" aria-labelledby="${modalId}ModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="col-md-4"></div>
                    <div class="col-md-4 d-flex justify-content-center">
                        <h2 class="modal-title" id="${modalId}Label">${modalId}</h2>
                    </div>
                    <div class="col-md-4 text-right">
                        <button type="button" data-bs-dismiss="modal" class="close" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                </div>
                <div class="modal-body" id="${modalId}Content">
                    ${content}
                </div>
            </div>
        </div>
    </div>`;

    // Append the modal to the body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Correctly reference the modal by its full ID including "Modal" suffix
    const modalElement = new bootstrap.Modal(document.getElementById(`${modalId}Modal`));

    // If the modal is for the profile, update its content dynamically
    if (modalId === 'Profile') {
        updateUserProfile();
    }
	
    // Return the modal element for further use if needed
    return modalElement;
}