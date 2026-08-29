

"use strict";

(function () {
    const STORAGE_KEY = "easy-projet-sidebar-collapsed";

    const sidebar = document.querySelector(
        "[data-sidebar]"
    );

    const toggleButton = document.querySelector(
        "[data-sidebar-toggle]"
    );

    if (!sidebar) {
        return;
    }

    function isCollapsed() {
        return (
            sidebar.dataset.sidebarCollapsed === "true"
        );
    }

    function renderState(collapsed) {
        sidebar.dataset.sidebarCollapsed = String(
            collapsed
        );

        toggleButton.setAttribute(
            "aria-expanded",
            String(!collapsed)
        );

        toggleButton.setAttribute(
            "aria-label",
            collapsed
                ? "Déployer le menu"
                : "Réduire le menu"
        );

        toggleButton.setAttribute(
            "title",
            collapsed
                ? "Déployer le menu"
                : "Réduire le menu"
        );

        const icon = toggleButton.querySelector(
            "[data-sidebar-toggle-icon]"
        );

        if (icon) {
            icon.setAttribute(
                "data-lucide",
                collapsed
                    ? "panel-left-open"
                    : "panel-left-close"
            );

            if (window.lucide) {
                window.lucide.createIcons();
            }
        }
    }

    function saveState(collapsed) {
        localStorage.setItem(
            STORAGE_KEY,
            collapsed ? "true" : "false"
        );
    }

    function loadState() {
        return (
            localStorage.getItem(STORAGE_KEY)
            === "true"
        );
    }

    if (toggleButton) {
        renderState(loadState());

        toggleButton.addEventListener(
            "click",
            function () {
                const collapsed = !isCollapsed();

                renderState(collapsed);
                saveState(collapsed);
            }
        );
    }

        // ------------------------------------------------------------
    // Menu utilisateur
    // ------------------------------------------------------------

    const userMenuContainer = document.querySelector(
        "[data-user-menu-container]"
    );

    const userMenuToggle = document.querySelector(
        "[data-user-menu-toggle]"
    );

    const userMenu = document.querySelector(
        "[data-user-menu]"
    );

    const userMenuChevron = document.querySelector(
        "[data-user-menu-chevron]"
    );

    function closeUserMenu() {
        if (!userMenu || !userMenuToggle) {
            return;
        }

        userMenu.classList.add("hidden");

        userMenuToggle.setAttribute(
            "aria-expanded",
            "false"
        );

        if (userMenuChevron) {
            userMenuChevron.classList.remove(
                "rotate-180"
            );
        }
    }

    function openUserMenu() {
        if (!userMenu || !userMenuToggle) {
            return;
        }

        userMenu.classList.remove("hidden");

        userMenuToggle.setAttribute(
            "aria-expanded",
            "true"
        );

        if (userMenuChevron) {
            userMenuChevron.classList.add(
                "rotate-180"
            );
        }
    }

    function isUserMenuOpen() {
        return (
            userMenu
            && !userMenu.classList.contains("hidden")
        );
    }

    if (
        userMenuContainer
        && userMenuToggle
        && userMenu
    ) {
        userMenuToggle.addEventListener(
            "click",
            function (event) {
                event.stopPropagation();

                if (isUserMenuOpen()) {
                    closeUserMenu();
                } else {
                    openUserMenu();
                }
            }
        );

        document.addEventListener(
            "click",
            function (event) {
                if (
                    !userMenuContainer.contains(
                        event.target
                    )
                ) {
                    closeUserMenu();
                }
            }
        );

        document.addEventListener(
            "keydown",
            function (event) {
                if (event.key === "Escape") {
                    closeUserMenu();
                    userMenuToggle.focus();
                }
            }
        );
    }
    
})();