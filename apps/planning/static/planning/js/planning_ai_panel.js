

"use strict";

(function () {
    const panel = document.querySelector(
        "[data-planning-ai-panel]"
    );

    const toggle = document.getElementById(
        "planning-ai-open-button"
    );

    if (!panel || !toggle) {
        return;
    }

    const closeButton = document.getElementById(
        "planning-ai-close-button"
    );

    function setOpen(isOpen) {
        panel.classList.toggle(
            "ep-communication-panel-open",
            isOpen
        );

        panel.setAttribute(
            "aria-hidden",
            isOpen ? "false" : "true"
        );

        toggle.setAttribute(
            "aria-expanded",
            isOpen ? "true" : "false"
        );
    }

    toggle.addEventListener(
        "click",
        function () {
            const isOpen = (
                panel.getAttribute("aria-hidden") === "false"
            );

            setOpen(!isOpen);
        }
    );

    if (closeButton) {
        closeButton.addEventListener(
            "click",
            function () {
                setOpen(false);
            }
        );
    }
}());