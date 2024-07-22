import '../scss/styles.scss'
import * as bootstrap from 'bootstrap'

export function createModal(modalId, modalTitle, content) {
    const modalHTML = `
    <div class="modal fade" id="${modalId}Modal" role="dialog" aria-labelledby="${modalId}ModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header row col-md-12">
                    <div class="col-md-4"></div>
                    <div class="col-md-4">
                        <h2 class="modal-title" id="${modalId}Label">${modalTitle}</h2>
                    </div>
                    <div class="col-md-4">
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

    // Return the modal element for further use if needed
    return modalElement;
}

export function createGameModal() {
    const modalHTML = `
    <div class="modal fade modal-static" id="pongModal" role="dialog" aria-labelledby="pongModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-game" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title" id="pongLabel">Local Game</h2>
                    <button type="button" data-bs-dismiss="modal" class="close" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body" id="pongContent">
                    <div class="pongContainer">
                        <div id="pongCanvas"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>`;

    // Append the modal to the body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Correctly reference the modal by its full ID including "Modal" suffix
    const modalElement = new bootstrap.Modal(document.getElementById(`pongModal`));

    // Return the modal element for further use if needed
    return modalElement;
}