

"use strict";

(function () {
    const STORAGE_KEY = "easy-projet-sidebar-collapsed";

    const sidebar = document.querySelector(
        "[data-sidebar]"
    );

    const toggleButton = document.querySelector(
        "[data-sidebar-toggle]"
    );

    if (!sidebar || !toggleButton) {
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

    renderState(loadState());

    toggleButton.addEventListener(
        "click",
        function () {
            const collapsed = !isCollapsed();

            renderState(collapsed);
            saveState(collapsed);
        }
    );
})();