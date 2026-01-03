function buildToggleSwitchElement(toggledOn=false, elementId=null) {
    const idAttribute = elementId !== null ? `id="${elementId}"` : '';

    const switchHTML = `
        <div
            toggle-switch-component
            class="toggle-switch-component${toggledOn ? ' active' : ''}"
            ${idAttribute}
        >
            <div class="toggle-switch-knob"></div>
        </div>
    `

    const switchEl = createElementFromHTML(switchHTML);

    switchEl.toggleSwitch = () => {
      switchEl.classList.toggle("active");

      const event = new CustomEvent("switchToggle", {
        detail: {
          active: switchEl.classList.contains("active"),
        },
      });

      switchEl.dispatchEvent(event);
    };

    switchEl.addEventListener("click", (event) => {
      // prevent parent element click events
      event.stopPropagation();

      // fire switch toggle event
      switchEl.toggleSwitch();
    });

    return switchEl
}
