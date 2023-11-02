function toggleExpand(element) {
  if (!element.style.height || element.style.height == "0px") {
    element.style.height =
    //   Array.prototype.reduce.call(
    //     element.childNodes,
    //     function (p, c) {
    //       return p + (c.offsetHeight || 0);
    //     },
    //     0
    //   ) + "px";
    // setTimeout(() => {
    //   element.style.height = 'auto';
    // }, 300);
      "auto";
  } else {
    element.style.height = "0px";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Select all email account containers
  const emailAccountContainers = Array.from(
    document.getElementsByClassName("email-account-container")
  );

  // setup logic for each email account
  emailAccountContainers.forEach((emailAccountContainer) => {
    const emailAddress = emailAccountContainer.getAttribute(
      "email-address-clear"
    );

    const emailAddressRedacted = emailAccountContainer.getAttribute(
      "email-address-redacted"
    );

    const emailAddressDisplayEl = emailAccountContainer.querySelector(
      "[email-address-display]"
    );

    // get top section for email account container
    const emailAccountInfoElement = emailAccountContainer.querySelector(
      ".email-account-info"
    );

    // SETTINGS SHOW / HIDE
    // get edit button for each email account container
    const emailAccountEditBtn =
      emailAccountContainer.querySelector("[edit-btn]");

    const emailAccountSettingsWrapper = emailAccountContainer.querySelector(
      ".email-account-settings-wrapper"
    );

    emailAccountInfoElement.addEventListener("click", (event) => {
      if (
        event.target === emailAccountInfoElement ||
        emailAccountEditBtn.contains(event.target)
      ) {
        // toggleExpand(emailAccountSettingsWrapper);
        emailAccountContainer.classList.toggle("active");
      }
    });

    // EMAIL ADDRESS TEXT VISIBLITY
    const emailTextVisbilityOnIcon = emailAccountInfoElement.querySelector(
      "[email-visibility-on]"
    );
    const emailTextVisbilityOffIcon = emailAccountInfoElement.querySelector(
      "[email-visibility-off]"
    );

    emailTextVisbilityOnIcon.addEventListener("click", () => {
      // set text visibility
      emailAddressDisplayEl.textContent = emailAddress;

      // swap show and hide buttons
      emailTextVisbilityOnIcon.style.display = "none";
      emailTextVisbilityOffIcon.style.display = "block";
    });

    emailTextVisbilityOffIcon.addEventListener("click", () => {
      // set text visibility
      emailAddressDisplayEl.textContent = emailAddressRedacted;

      // swap show and hide buttons
      emailTextVisbilityOffIcon.style.display = "none";
      emailTextVisbilityOnIcon.style.display = "block";
    });

    // WHITELIST TOGGLE
    const emailWhitelistToggleElement = emailAccountContainer.querySelector(
      "[email-whitelist-toggle-switch]"
    );

    const switchElement = emailWhitelistToggleElement.querySelector(
      "[toggle-switch-component]"
    );

    // toggle inner switch when outer container is clicked
    emailWhitelistToggleElement.addEventListener("click", () => {
      switchElement.toggleSwitch();
    });

    switchElement.addEventListener("switchToggle", (event) => {
      console.log(
        `toggling whitelist ${event.detail.active} for ${emailAddress}`
      );
    });


    // SETTINGS VIEWS
    // get all settings buttons that reference a different settings view
    const viewsItemThatReference = Array.from(
      emailAccountSettingsWrapper.querySelectorAll('[references]')
    );

    viewsItemThatReference.forEach((viewItemThatReferences) => {
      // get parent element that the view item is a child of
      const parentElement = emailAccountSettingsWrapper.querySelector(
        `[setting="${viewItemThatReferences.getAttribute('parent-setting')}"]`
      );

      // get settings view that the current settings view item references
      const referencedElement = emailAccountSettingsWrapper.querySelector(
        `[setting="${viewItemThatReferences.getAttribute('references')}"]`
      );

      // go to the referenced element on click
      viewItemThatReferences.addEventListener('click', () => {
        parentElement.classList.remove('active');
        referencedElement.classList.add('active');
      });

    });

  });
});
