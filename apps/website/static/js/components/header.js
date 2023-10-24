function setupUserMenu() {
    // get user menu button
    const userMenuButton = document.getElementById('navbar-user-menu-button');

    // show button and set image to user's profile picture
    userMenuButton.style.display = 'block';
    userMenuButton.src = userData.avatar_url;

    // setup menu
    const userMenuEl = document.getElementById('navbar-user-menu');

    userMenuButton.addEventListener('click', () => {
        userMenuEl.classList.toggle('active');
    })

    // When the user clicks anywhere outside of the menu, close it
    window.addEventListener('click', (event) => {
        // make sure user is not clicking on menu or toggle button
        if (!userMenuEl.contains(event.target) && !userMenuButton.contains(event.target)) {
            userMenuEl.classList.remove('active');
            }

    })
}


const userData = contextData.user;

if (userData != null && userData != undefined) {
    // set user menu in navbar
    setupUserMenu();
} else {
    // show login button
    const loginButtonEl = document.getElementById('navbar-login-button');
    loginButtonEl.style.display = 'block';
}


// hamburger menu
const navlinksElement = document.getElementById('navbar-navlinks');

const navbarHamburgerIcon = document.getElementById('navbar-hamburger-icon');
navbarHamburgerIcon.addEventListener('click', () => {
    navbarHamburgerIcon.classList.toggle('open');
    navlinksElement.classList.toggle('open');
})
