export function showMessage(message, modalId, type = 'error') {
    // Determine the CSS class based on the message type
    const messageClass = type === 'accept' ? 'AcceptMessage' : 'ErrorMessage';

    // Remove any existing message of the same type
    const existingMessage = document.querySelector(`${modalId} .${messageClass}`);
    if (existingMessage) {
        existingMessage.remove();
    }

    // Create a span element for the message
    var messageSpan = document.createElement('span');
    messageSpan.classList.add(messageClass);
    messageSpan.textContent = message;

    // Insert the message before the modal body
    var modalBody = document.querySelector(`${modalId} .modal-body`);
    modalBody.parentNode.insertBefore(messageSpan, modalBody);

    // Hide the message after 5 seconds
    setTimeout(function () {
        if (messageSpan && messageSpan.parentNode) {
            messageSpan.parentNode.removeChild(messageSpan);
        }
    }, 2500);
}
