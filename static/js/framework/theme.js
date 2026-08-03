


"use strict";

(function () {
    const STORAGE_KEY = "easy-projet-theme";
    const VALID_THEMES = new Set([
        "system",
        "light",
        "dark",
    ]);

    const systemDarkQuery = window.matchMedia(
        "(prefers-color-scheme: dark)"
    );

    function getStoredTheme() {
        const storedTheme = window.localStorage.getItem(
            STORAGE_KEY
        );

        if (VALID_THEMES.has(storedTheme)) {
            return storedTheme;
        }

        return "system";
    }

    function getEffectiveTheme(theme) {
        if (theme === "system") {
            return systemDarkQuery.matches
                ? "dark"
                : "light";
        }

        return theme;
    }

    function applyTheme(theme) {
        const effectiveTheme = getEffectiveTheme(theme);

        document.documentElement.classList.toggle(
            "dark",
            effectiveTheme === "dark"
        );

        document.documentElement.dataset.theme = theme;
    }

    function updateMenuState(theme) {
        document
            .querySelectorAll("[data-theme-check]")
            .forEach(function (checkIcon) {
                checkIcon.classList.toggle(
                    "hidden",
                    checkIcon.dataset.themeCheck !== theme
                );
            });

        const themeIcon = document.querySelector(
            "[data-theme-icon]"
        );

        if (!themeIcon) {
            return;
        }

        const iconName = {
            system: "monitor",
            light: "sun",
            dark: "moon",
        }[theme];

        themeIcon.setAttribute(
            "data-lucide",
            iconName
        );

        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    function setTheme(theme) {
        if (!VALID_THEMES.has(theme)) {
            return;
        }

        window.localStorage.setItem(
            STORAGE_KEY,
            theme
        );

        applyTheme(theme);
        updateMenuState(theme);
    }

    function closeMenu(menu) {
        const dropdown = menu.querySelector(
            "[data-theme-dropdown]"
        );

        const trigger = menu.querySelector(
            "[data-theme-trigger]"
        );

        if (!dropdown || !trigger) {
            return;
        }

        dropdown.classList.add("hidden");
        trigger.setAttribute(
            "aria-expanded",
            "false"
        );
    }

    function openMenu(menu) {
        const dropdown = menu.querySelector(
            "[data-theme-dropdown]"
        );

        const trigger = menu.querySelector(
            "[data-theme-trigger]"
        );

        if (!dropdown || !trigger) {
            return;
        }

        dropdown.classList.remove("hidden");
        trigger.setAttribute(
            "aria-expanded",
            "true"
        );
    }

    function initializeThemeMenu() {
        const menu = document.querySelector(
            "[data-theme-menu]"
        );

        if (!menu) {
            return;
        }

        const trigger = menu.querySelector(
            "[data-theme-trigger]"
        );

        const dropdown = menu.querySelector(
            "[data-theme-dropdown]"
        );

        if (!trigger || !dropdown) {
            return;
        }

        trigger.addEventListener(
            "click",
            function (event) {
                event.stopPropagation();

                if (
                    dropdown.classList.contains("hidden")
                ) {
                    openMenu(menu);
                } else {
                    closeMenu(menu);
                }
            }
        );

        menu
            .querySelectorAll("[data-theme-option]")
            .forEach(function (option) {
                option.addEventListener(
                    "click",
                    function () {
                        setTheme(
                            option.dataset.themeOption
                        );

                        closeMenu(menu);
                    }
                );
            });

        document.addEventListener(
            "click",
            function (event) {
                if (!menu.contains(event.target)) {
                    closeMenu(menu);
                }
            }
        );

        document.addEventListener(
            "keydown",
            function (event) {
                if (event.key === "Escape") {
                    closeMenu(menu);
                    trigger.focus();
                }
            }
        );
    }

    function initializeTheme() {
        const theme = getStoredTheme();

        applyTheme(theme);
        updateMenuState(theme);
        initializeThemeMenu();
    }

    systemDarkQuery.addEventListener(
        "change",
        function () {
            const theme = getStoredTheme();

            if (theme === "system") {
                applyTheme(theme);
            }
        }
    );

    document.addEventListener(
        "DOMContentLoaded",
        initializeTheme
    );
})();