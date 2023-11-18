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

// REQUEST FUNCTIONS
async function requestRemoveWhitelistedSender(emailAccountData, whitelistedSenderEmailAddress) {
  const response = await fetch("/dashboard/api/remove-whitelisted-sender", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      {
        email_account_data: emailAccountData,
        sender_email_address: whitelistedSenderEmailAddress
      }
    ),
  });

  const data = await response.json();
  return data;
}

async function requestAddWhitelistedSender(emailAccountData, whitelistedSenderEmailAddress) {
  const response = await fetch("/dashboard/api/add-whitelisted-sender", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      {
        email_account_data: emailAccountData,
        sender_email_address: whitelistedSenderEmailAddress
      }
    ),
  });
  const data = await response.json();
  return data;
}

async function requestToggleSenderWhitelist(emailAccountData, enabled) {
  const response = await fetch("/dashboard/api/toggle-sender-whitelist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      {
        email_account_data: emailAccountData,
        enabled: enabled
      }
    ),
  });

  const data = await response.json();
  return data
}

async function requestRemoveEmailAccount(emailAccountData) {
  const response = await fetch("/dashboard/api/remove-email-account", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      {
        email_account_data: emailAccountData,
      }
    ),
  });
  const data = await response.json();
  return data;
}

// BUILD EMAIL ACCOUNT ELEMENTS
function buildWhitelistedSenderElement(whitelistedSenderEmailAddress, emailAccountData) {
  const whitelistedSenderElement = createElementFromHTML(`
    <div class="listed-email">
      <div class="email-text-container">
        <p class="email-text">${whitelistedSenderEmailAddress}</p>
      </div>
      <div class="email-text-context-menu-wrapper">
        <iconify-icon
          context-menu-toggle-button
          class="email-options-btn circular-button light-hover-overlay"
          icon="tabler:dots"
        ></iconify-icon>

        <div class="context-menu">
          <div class="context-menu-section">
            <a action="edit" class="context-menu-option light-hover-overlay">
              <iconify-icon icon="ic:baseline-edit"></iconify-icon>
              <span>Edit</span>
            </a>
            <a action="delete" class="context-menu-option light-hover-overlay">
              <iconify-icon icon="iconamoon:trash-fill"></iconify-icon>
              <span>Delete</span>
            </a>
          </div>
        </div>

      </div>
    </div>
  `)

  // setup context menu and it's buttons
  const toggleBtn = whitelistedSenderElement.querySelector(
    '[context-menu-toggle-button]'
  );

  const contextMenu = whitelistedSenderElement.querySelector(
    '.context-menu'
  );

  toggleBtn.addEventListener('click', () => {
    // toggle context menu
    const position = toggleBtn.getBoundingClientRect();

    contextMenu.style.top = `${position.top}px`;

    contextMenu.classList.toggle('active');
  });

  // hide context menu when clicking elsewhere
  window.addEventListener('click', (event) => {
    // make sure user is not clicking on menu or toggle button
    if (!contextMenu.contains(event.target) && !toggleBtn.contains(event.target)) {
      contextMenu.classList.remove('active');
    }
  });

  // actions
  const deleteBtn = contextMenu.querySelector('[action=delete]');
  deleteBtn.addEventListener('click', () => {
    whitelistedSenderElement.remove();
    console.log(
      `Deleting whitelisted sender "${whitelistedSenderEmailAddress}"`,
      `from email account "${emailAccountData.email_address}"`
    );
    requestRemoveWhitelistedSender(emailAccountData, whitelistedSenderEmailAddress);
  });

  return whitelistedSenderElement
}


function setupEmailAccountToggleSwitches(emailAccountContainer, emailAccountData) {
  // setup toggle switches
  const toggleSwitchElements = Array.from(
    emailAccountContainer.querySelectorAll('[toggle-switch-placeholder]')
  );

  toggleSwitchElements.forEach((toggleSwitchPlaceholder) => {
    // create toggle switch and replace placeholder toggle switch placeholder element
    const toggleSwitchElement = buildToggleSwitchElement(
      emailAccountData.sender_whitelist.enabled
    );

    replaceElement(toggleSwitchPlaceholder, toggleSwitchElement);
  });
}


function setupSenderWhitelistToggleSwitchActions(emailAccountContainer, emailAccountData) {
  // TOGGLE EFFECTS
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

  // handle toggle switch action
  switchElement.addEventListener("switchToggle", (event) => {
    console.log(
      `toggling whitelist ${event.detail.active} for ${emailAccountData.email_address}`
    );
    requestToggleSenderWhitelist(emailAccountData, event.detail.active);
  });
}


function setupAddWhitelistedSenderModal(emailAccountContainer, emailAccountData) {
  const senderWhitelistContainer = emailAccountContainer.querySelector(
    'div[sender-whitelist-container]'
  );

  const senderWhitelistAddBtn = emailAccountContainer.querySelector(
    '[sender-whitelist-add-btn]'
  );

  const senderWhitelistModal = getModal(
    'add-whitelisted-sender-modal'
  );

  const contextData = {
    emailAccountData: emailAccountData,
    senderWhitelistContainer: senderWhitelistContainer
  };

  senderWhitelistAddBtn.addEventListener('click', () => {
    // open modal to enter email address
    openModal(senderWhitelistModal, contextData);
  });
}


function addWhitelistedSenderElements(emailAccountContainer, emailAccountData) {
  const senderWhitelistContainer = emailAccountContainer.querySelector(
    "[sender-whitelist-container]"
  );

  for (let i = 1; i < 150; i++) {
    const whitelistedSenderElement = buildWhitelistedSenderElement(
      `emailaddress-${i}`);
    senderWhitelistContainer.appendChild(whitelistedSenderElement);
  }

  emailAccountData.sender_whitelist.whitelisted_senders.forEach((whitelisted_sender) => {
    // build and add whitelisted sender element
    const whitelistedSenderElement = buildWhitelistedSenderElement(
      whitelisted_sender, emailAccountData
    );

    senderWhitelistContainer.appendChild(whitelistedSenderElement);
  });
}


// REMOVE EMAIL ACCOUNT
const removeEmailAccountConfirmationModal = document.getElementById(
  'confirm-delete-email-account-modal'
);

removeEmailAccountConfirmationModal.addEventListener('confirm', () => {
  const emailAccountData =
    removeEmailAccountConfirmationModal.contextData.emailAccountData;

  const emailAccountContainer =
    removeEmailAccountConfirmationModal.contextData.emailAccountContainer;

  requestRemoveEmailAccount(emailAccountData).then(data => {
    if (data.success === true) {
      // close modal and remove element if successful
      closeModal(removeEmailAccountConfirmationModal);
      emailAccountContainer.remove();
    } else {
      // set message
      stopModalLoading(removeEmailAccountConfirmationModal);
      setModalResponseMsg(removeEmailAccountConfirmationModal, data);
    }
  });

  console.log(`Removed email account ${emailAccountData.email_address}`);
});


function setupEmailAccountContainerButtons(emailAccountContainer, emailAccountData) {
  // displays email account address as well as buttons
  const emailAccountInfoElement = emailAccountContainer.querySelector(
    ".email-account-info"
  );

  // EMAIL ADDRESS TEXT VISIBILITY
  const emailAddressDisplayText = emailAccountContainer.querySelector(
    "[email-display]"
  );

  const emailTextVisbilityOnIcon = emailAccountInfoElement.querySelector(
    "[email-visibility-on]"
  );
  const emailTextVisbilityOffIcon = emailAccountInfoElement.querySelector(
    "[email-visibility-off]"
  );

  emailTextVisbilityOnIcon.addEventListener("click", () => {
    // set text visibility
    emailAddressDisplayText.textContent = emailAccountData.email_address;

    // swap show and hide buttons
    emailTextVisbilityOnIcon.style.display = "none";
    emailTextVisbilityOffIcon.style.display = "block";
  });

  emailTextVisbilityOffIcon.addEventListener("click", () => {
    // set text visibility
    emailAddressDisplayText.textContent = emailAccountData.email_address_redacted;

    // swap show and hide buttons
    emailTextVisbilityOffIcon.style.display = "none";
    emailTextVisbilityOnIcon.style.display = "block";
  });

  // SETTINGS BTN
  const emailAccountEditBtn =
    emailAccountContainer.querySelector("[edit-btn]");

  emailAccountInfoElement.addEventListener("click", (event) => {
    if (
      event.target === emailAccountInfoElement
        || emailAccountEditBtn.contains(event.target)
    ) {
      emailAccountContainer.classList.toggle("active");
    }
  });


  // REMOVE EMAIL ACCOUNT BTN
  const emailAccountDeleteBtn = emailAccountContainer.querySelector(
    '[delete-btn]'
  );

  emailAccountDeleteBtn.addEventListener('click', () => {
    // set modal description to
    const modalDescriptionElement = removeEmailAccountConfirmationModal.querySelector(
      '.modal-description'
    );

    modalDescriptionElement.innerHTML =
      `Are you sure would like to remove the email account <code>${emailAccountData.email_address}</code>?`;


    openModal(
      removeEmailAccountConfirmationModal,
      {
        emailAccountData: emailAccountData,
        emailAccountContainer: emailAccountContainer
      }
    );
  });

  // close all active context menus on scroll
  const settingsViews = Array.from(
    emailAccountContainer.getElementsByClassName('email-account-settings'
  ));

  settingsViews.forEach(settingsView => {
    settingsView.addEventListener('scroll', () => {
      const contextMenus = Array.from(
        settingsView.querySelectorAll('.context-menu.active')
      );

      contextMenus.forEach(contextMenu => {
        contextMenu.classList.remove('active');
      });
    });
  });
}


function setupSettingsViews(emailAccountContainer) {
  const emailAccountSettingsWrapper = emailAccountContainer.querySelector(
    ".email-account-settings-wrapper"
  );

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
}


function buildEmailAccountElement(emailAccountData) {
  const emailAccountElement = createElementFromHTML(`
    <div class="container-content">
      <div
        class="email-account-container"
        email-account-type="${emailAccountData.webmail_service}"
      >
        <div class="email-account-info">

          <p>
            <span email-display>${emailAccountData.email_address_redacted}</span>
            <iconify-icon
              visibility-icon
              email-visibility-off
              class="circular-button light-hover-overlay"
              icon="mdi:visibility-off"
            ></iconify-icon>
            <iconify-icon
              visibility-icon
              email-visibility-on
              class="circular-button light-hover-overlay"
              icon="mdi:visibility"
            ></iconify-icon>
          </p>

          <div class="email-account-buttons">
            <p edit-btn class="email-account-edit-btn circular-button light-hover-overlay">
              <iconify-icon icon="mdi:cog"></iconify-icon>
            </p>

            <p delete-btn class="email-account-delete-btn circular-button light-hover-overlay">
              <iconify-icon icon="iconamoon:trash-fill"></iconify-icon>
            </p>
          </div>

        </div>

        <div class="email-account-settings-wrapper">

          <div
            setting="primary-settings"
            class="email-account-settings primary-view active"
          >
            <div
              email-whitelist-toggle-switch
              class="email-account-settings-option light-hover-overlay"
            >
              <div class="settings-option-text-container">
                <p class="settings-option-title">Sender Whitelist</p>
              </div>
              <div toggle-switch-placeholder></div>
            </div>

            <div
              references="manage-sender-whitelist"
              parent-setting="primary-settings"
              class="email-account-settings-option light-hover-overlay"
            >
              <div class="settings-option-text-container">
                <p class="settings-option-title">Manage Sender Whitelist</p>
                <p class="settings-option-description">
                  Customize which emails you recieve notifications for by whitelisting certain senders
                </p>
              </div>
              <iconify-icon icon="mingcute:right-line"></iconify-icon>
            </div>
          </div>

          <div
            setting="manage-sender-whitelist"
            class="email-account-settings secondary-view"
          >
            <div class="email-account-settings-list-top">
              <p
                references="primary-settings"
                parent-setting="manage-sender-whitelist"
                class="back-arrow"
              >
                <iconify-icon class="circular-button light-hover-overlay" icon="octicon:arrow-left-24"></iconify-icon>
                <span>Manage Sender Whitelist</span>
              </p>
              <p class="small-new-button circular-button light-hover-overlay" sender-whitelist-add-btn>
                <iconify-icon icon="fluent:add-28-regular"></iconify-icon>
              </p>
            </div>

            <div sender-whitelist-container class="listed-email-container">

            </div>
          </div>
        </div>

      </div>
    </div>
  `);

  const emailAccountContainer = emailAccountElement.querySelector(
    '.email-account-container'
  );

  setupEmailAccountToggleSwitches(emailAccountContainer, emailAccountData);
  setupAddWhitelistedSenderModal(emailAccountContainer, emailAccountData);

  addWhitelistedSenderElements(emailAccountContainer, emailAccountData);

  setupEmailAccountContainerButtons(emailAccountContainer, emailAccountData);

  setupSenderWhitelistToggleSwitchActions(emailAccountContainer, emailAccountData);
  setupSettingsViews(emailAccountContainer);

  return emailAccountElement;
}


document.addEventListener("DOMContentLoaded", () => {
  // add shit to the DOM based on data from backend
  const emailAccountsData = contextData.user.email_accounts;

  const emailAccServiceElRegistry = {};

  // gmail email accounts
  emailAccountsData.forEach((emailAccountData) => {
    // build email account
    const emailAccountElement = buildEmailAccountElement(emailAccountData);

    const webmailService = emailAccountData.webmail_service;
    let emailAccServiceContainerEl;

    if (emailAccServiceElRegistry[webmailService] === undefined) {
      // obtain element and add it to the registry directly
      emailAccServiceContainerEl = document.querySelector(
        `[webmail-service="${webmailService}"]`
      );

      emailAccServiceElRegistry[webmailService] = emailAccServiceContainerEl;
    } else {
      // obtain element from registry directly
      emailAccServiceContainerEl = emailAccServiceElRegistry[webmailService];
    }

    // add email account to container element
    emailAccServiceContainerEl.appendChild(emailAccountElement);
  });


  // SENDER WHITELIST MODAL
  const senderWhitelistModal = getModal('add-whitelisted-sender-modal');

  // handle input submissions
  senderWhitelistModal.addEventListener('inputSubmit', (event) => {
    modalContextData = senderWhitelistModal.contextData;
    // get corresponding email address from modal context data
    const emailAddress = modalContextData.emailAccountData.email_address;

    const inputValue = event.detail.value;
    console.log(`Adding ${inputValue} to sender whitelist of ${emailAddress}`);
    requestAddWhitelistedSender(modalContextData.emailAccountData, inputValue)
      .then(data => {
        if (data.success === true) {
          senderWhitelistModal.close();

          // add newly whitelisted sender to whitelisted sender element
          const senderWhitelistContainer = modalContextData.senderWhitelistContainer;

          const whitelistedSenderElement = buildWhitelistedSenderElement(
            inputValue, modalContextData.emailAccountData
          );
          senderWhitelistContainer.appendChild(whitelistedSenderElement);
        } else {
          stopModalLoading(senderWhitelistModal);
          setModalResponseMsg(senderWhitelistModal, data);
        }
      });
  });
});