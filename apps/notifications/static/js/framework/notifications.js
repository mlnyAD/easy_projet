document.addEventListener("DOMContentLoaded", function () {
    const menu = document.querySelector("[data-notification-menu]");

    if (!menu) {
        return;
    }

    const trigger = menu.querySelector("[data-notification-trigger]");
    const dropdown = menu.querySelector("[data-notification-dropdown]");

    if (!trigger || !dropdown) {
        return;
    }

    function closeMenu() {
        dropdown.classList.add("hidden");
        trigger.setAttribute("aria-expanded", "false");
    }

    trigger.addEventListener("click", function () {
        const isOpen = !dropdown.classList.contains("hidden");

        if (isOpen) {
            closeMenu();
            return;
        }

        dropdown.classList.remove("hidden");
        trigger.setAttribute("aria-expanded", "true");
    });

    document.addEventListener("click", function (event) {
        if (!menu.contains(event.target)) {
            closeMenu();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeMenu();
        }
    });
});
