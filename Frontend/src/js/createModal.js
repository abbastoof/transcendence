import * as bootstrap from 'bootstrap'

export function createModal(modalId, modalTitle, content) {
    const modalHTML = `
    <div class="modal fade" id="${modalId}Modal" tabindex="-1" role="dialog" data-bs-backdrop="static" aria-labelledby="${modalId}Label" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title" id="${modalId}Label">${modalTitle}</h2>
                    <button type="button" id="${modalId}Close" data-bs-dismiss="modal" class="close" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
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

    // Function to show the modal and set URL hash
    function showModal() {
        modalElement.show();
        if (window.location.hash !== `#${modalId}`) {
            history.pushState({ modalId: modalId }, null, `#${modalId}`);
        }
    }

    // Function to hide the modal and clear URL hash
    function hideModal() {
        modalElement.hide();
        if (window.location.hash === `#${modalId}`) {
            history.pushState(null, null, ' ');
        }
    }

    // Add event listener to hidden modal and clear URL hash when modal is hidden
    modalElement._element.addEventListener('hidden.bs.modal', function () {
        if (window.location.hash === `#${modalId}`) {
            history.back();
        }
    });

    // Add event listener to set URL hash when modal is shown
    modalElement._element.addEventListener('shown.bs.modal', function () {
        if (window.location.hash !== `#${modalId}`) {
            window.location.hash = modalId;
        }
    });

    // Listen for hashchange events to handle back/forward navigation
    window.addEventListener('hashchange', function () {
        if (window.location.hash === `#${modalId}`) {
            modalElement.show();
        } else {
            modalElement.hide();
        }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === "Escape") {
            modalElement.hide();
        }
    });

    // Optionally, handle the initial load if the URL contains the modal hash
    if (window.location.hash === `#${modalId}`) {
        modalElement.show();
    }

    // Return the modal element and show/hide functions for further use if needed
    return {
        modalElement,
        showModal,
        hideModal
    };
}
