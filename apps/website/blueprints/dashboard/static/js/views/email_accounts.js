document.addEventListener('DOMContentLoaded', () => {
    const emailWhitelistToggleElements =
        document.querySelectorAll('[email-whitelist-toggle-switch]');

    emailWhitelistToggleElements.forEach((el) => {
        const switchElement = el.querySelector('[toggle-switch-component]');

        // toggle inner switch when outer container is clicked
        el.addEventListener('click', () => {
            switchElement.toggleSwitch();
        });

        switchElement.addEventListener('switchToggle', (event) => {
            const emailAddress = el.getAttribute('email-address');
            console.log(`toggling whitelist ${event.detail.active} for ${emailAddress}`);
        });
    });
});
