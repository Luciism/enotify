function setActiveViewButton(viewName) {
    // remove active class from any active view buttons
    sidebarViewBtns.forEach((viewBtn) => {
        if (viewBtn.classList.contains('active')) {
            viewBtn.classList.remove('active')
        }
    });

    // add active class to correct button
    sidebarViewBtnMap[viewName].classList.add('active');
}

function setActiveDashboardView(viewName) {
    // remove active class from any active views
    views.forEach((viewEl) => {
        if (viewEl.classList.contains('active')) {
            viewEl.classList.remove('active')
        }
    });

    // add active class to correct view
    viewMap[viewName].classList.add('active');
}

function switchDashboardView(viewName) {
    setActiveViewButton(viewName);
    setActiveDashboardView(viewName);
}


// map of view name to view element
const viewMap = {};

const views = Array.from(
    document.getElementsByClassName('dashboard-view')
);

views.forEach((viewEl) => {
    const viewName = viewEl.getAttribute('view');
    viewMap[viewName] = viewEl;
});


// map of view name to view button element
const sidebarViewBtnMap = {};

const sidebarViewBtns = Array.from(
    document.getElementsByClassName('sidebar-button')
);

sidebarViewBtns.forEach((viewButton) => {
    // select view attribute from element and map it to element
    const viewName = viewButton.getAttribute('view-btn');

    if (viewName != null) {
        sidebarViewBtnMap[viewName] = viewButton;

        // switch dashboard view on click
        viewButton.addEventListener("click", () => {
            switchDashboardView(viewName);
        })
    }
});


// set default active view to first view
const firstKey = Object.keys(viewMap)[0];
switchDashboardView(firstKey);


// sidebar toggling for mobile
const sidebar = document.getElementById('sidebar');
const sidebarToggleButton = document.getElementById('sidebar-toggle-btn');

sidebarToggleButton.addEventListener('click', () => {
    sidebar.classList.toggle('open');
});
