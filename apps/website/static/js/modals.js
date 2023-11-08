function getModal(modalId) {
    return document.getElementById(modalId);
}

function openModal(modalElement, contextData=undefined) {
    modalElement.contextData = contextData;
    modalElement.classList.add('active');

    if (modalElement.getAttribute('modal-type') === 'input') {
        // clear any existing input value
        modalElement.clearInput();

        // focus input element
        modalElement.querySelector('input').focus();
    }
}

function closeModal(modalElement) {
    modalElement.classList.remove('active');
    modalElement.contextData = undefined;
}

function toggleModal(modalElement) {
    modalElement.classList.toggle('active');
}

function clearInput(inputElement) {
    inputElement.value = null;
}

function handleInputModal(modalElement) {
    const inputElement = modalElement.querySelector('input');

    // clear input field method
    modalElement.clearInput = () => {
        clearInput(inputElement);
    }

    // dispatch event containing input value
    function dispatchInputSubmitEvent() {
        const inputSubmitEvent = new CustomEvent("inputSubmit", {
            detail: {
              value: inputElement.value.toLocaleLowerCase()
            }
        });

        modalElement.dispatchEvent(inputSubmitEvent);
    }

    // submit when pressing enter input
    inputElement.addEventListener('keydown', (event) => {
        if (event.key == 'Enter') {
            event.preventDefault();
            dispatchInputSubmitEvent();
        }
    });

    // submit when button is pressed
    const submitBtn = modalElement.querySelector('button[type="submit"]');
    submitBtn.addEventListener('click', () => {
        dispatchInputSubmitEvent();
    });
}


document.addEventListener('DOMContentLoaded', () => {
    const modalElements = Array.from(
        document.getElementsByClassName('modal-wrapper')
    );

    modalElements.forEach((modalElement) => {
        // add custom properties
        modalElement.close = () => {
            closeModal(modalElement);
        }
        modalElement.open = () => {
            openModal(modalElement);
        }
        modalElement.toggle = () => {
            toggleModal(modalElement);
        }

        // get button to close modal
        const modalCloseBtn = modalElement.querySelector('.close-btn');

        // close modal if user clicks outside modal content or on close button
        modalElement.addEventListener('mousedown', (event) => {
            if (event.target == modalElement || event.target == modalCloseBtn) {
                modalElement.close();
            }
        });

        // handle different modal functionalities
        const modalType = modalElement.getAttribute('modal-type');

        if (modalType === 'input') {
            handleInputModal(modalElement);
        }
    });
});
