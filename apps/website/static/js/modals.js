// dispatch modal confirmation to any active confirmation modal when enter is pressed
document.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        const activeConfirmationModal = document.querySelector(
            'div.modal-wrapper.active[modal-type="confirmation"]'
        );

        if (activeConfirmationModal !== null) {
            activeConfirmationModal.dispatchConfirmationEvent();
        }
    }
});


function setModalHeading(modalElement, headingText) {
    const headingElement = modalElement.querySelector('.modal-heading');
    headingElement.textContent = headingText;
}

function setModalDescription(modalElement, descriptionText) {
    const descriptionElement = modalElement.querySelector('.modal-description');
    descriptionElement.textContent = descriptionText;
}

function setModalResponseMsg(modalElement, inputNoteData) {
    const responseMsgElement = modalElement.querySelector('[response-msg]');

    if (responseMsgElement !== null) {
        responseMsgElement.style.color = inputNoteData.color;
        responseMsgElement.textContent = inputNoteData.message;
        responseMsgElement.classList.add('show');
    }
}

function removeModalResponseMsg(modalElement) {
    const responseMsgElement = modalElement.querySelector('[response-msg]');

    if (responseMsgElement !== null) {
        responseMsgElement.textContent = '';
        responseMsgElement.classList.remove('show');
    }
}

function startModalLoading(modalElement) {
    const submitBtn = modalElement.querySelector('[submit-btn]');
    submitBtn.classList.add('loading');
}

function stopModalLoading(modalElement) {
    const submitBtn = modalElement.querySelector('[submit-btn]');
    submitBtn.classList.remove('loading');
}

function getModal(modalId) {
    return document.getElementById(modalId);
}

function openModal(modalElement, contextData=undefined) {
    modalElement.contextData = contextData;
    modalElement.classList.add('active');
    removeModalResponseMsg(modalElement);

    stopModalLoading(modalElement);

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
    const submitBtn = modalElement.querySelector('[submit-btn]');

    // clear input field method
    modalElement.clearInput = () => {
        clearInput(inputElement);
    }

    // dispatch event containing input value
    dispatchInputSubmitEvent = () => {
        submitBtn.classList.add('loading');

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
    submitBtn.addEventListener('click', () => {
        dispatchInputSubmitEvent();
    });
}

function handleConfirmationModal(modalElement) {
    const submitBtn = modalElement.querySelector('[submit-btn]');

    modalElement.dispatchConfirmationEvent = () => {
        const inputSubmitEvent = new CustomEvent("confirm");
        modalElement.dispatchEvent(inputSubmitEvent);

        submitBtn.classList.add('loading');
        // console.log('event dispatched');
        // modalElement.close();
    }

    // submit when button is pressed
    submitBtn.addEventListener('click', () => {
        modalElement.dispatchConfirmationEvent();
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

        modalElement.setHeading = (headingText) => {
            setModalHeading(modalElement, headingText);
        }

        modalElement.setDescription = (descriptionText) => {
            setModalDescription(modalElement, descriptionText);
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

        if (modalType === 'confirmation') {
            handleConfirmationModal(modalElement);
        }
    });
});
