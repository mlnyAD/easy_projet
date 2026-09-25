

"use strict";

(function () {
    const panel = document.querySelector(
        "[data-communication-panel]"
    );

    const toggle = document.querySelector(
        "[data-communication-toggle]"
    );

    if (!panel || !toggle) {
        return;
    }

    const closeButton = panel.querySelector(
        "[data-communication-close]"
    );
    const pinButton = panel.querySelector(
        "[data-communication-pin]"
    );
    const pinIcon = panel.querySelector(
        "[data-communication-pin-icon]"
    );
    const thread = panel.querySelector(
        "[data-communication-thread]"
    );
    const form = panel.querySelector(
        "[data-communication-form]"
    );
    const composerToggle = panel.querySelector(
        "[data-communication-composer-toggle]"
    );
    const composerContent = panel.querySelector(
        "[data-communication-composer-content]"
    );
    const composerIcon = panel.querySelector(
        "[data-communication-composer-toggle-icon]"
    );
    const input = panel.querySelector(
        "[data-communication-input]"
    );
    const subject = panel.querySelector(
        "[data-communication-subject]"
    );
    const errorBox = panel.querySelector(
        "[data-communication-error]"
    );
    const submitButton = panel.querySelector(
        "[data-communication-submit]"
    );
    const fileInput = panel.querySelector(
        "[data-communication-file-input]"
    );
    const fileButton = panel.querySelector(
        "[data-communication-file-button]"
    );
    const selectedFiles = panel.querySelector(
        "[data-communication-selected-files]"
    );
    const appMain = panel.closest(".ep-app-main");
    const pinnedStorageKey = (
        "easy-projet-communication-pinned"
    );
    const desktopMedia = window.matchMedia(
        "(min-width: 1024px)"
    );

    function refreshIcons() {
        if (
            window.lucide
            && typeof window.lucide.createIcons === "function"
        ) {
            window.lucide.createIcons();
        }
    }

    function scrollToBottom() {
        if (thread) {
            thread.scrollTop = thread.scrollHeight;
        }
    }

    function isPinned() {
        return panel.classList.contains(
            "ep-communication-panel-pinned"
        );
    }

    function setOpen(isOpen) {
        if (isPinned() && desktopMedia.matches) {
            isOpen = true;
        }

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

        if (isOpen) {
            scrollToBottom();
            markMessagesRead();
        }
    }

    function setPinned(pinned, persist) {
        if (!desktopMedia.matches) {
            pinned = false;
        }

        panel.classList.toggle(
            "ep-communication-panel-pinned",
            pinned
        );

        if (appMain) {
            appMain.classList.toggle(
                "ep-app-main-communication-pinned",
                pinned
            );
        }

        if (pinButton) {
            pinButton.setAttribute(
                "aria-pressed",
                pinned ? "true" : "false"
            );

            pinButton.setAttribute(
                "aria-label",
                pinned
                    ? "Désépingler le volet"
                    : "Épingler le volet"
            );

            pinButton.title = pinned
                ? "Désépingler le volet"
                : "Épingler le volet";

            pinButton.innerHTML = (
                '<i '
                + 'data-lucide="'
                + (pinned ? "pin" : "pin-off")
                + '" '
                + 'class="ep-communication-panel-icon" '
                + 'aria-hidden="true" '
                + 'data-communication-pin-icon'
                + '></i>'
            );
        }
        
        if (pinned) {
            setOpen(true);
        }

        if (persist) {
            localStorage.setItem(
                pinnedStorageKey,
                pinned ? "true" : "false"
            );
        }

        refreshIcons();
    }

    function setComposerOpen(isOpen) {
        if (!composerToggle || !composerContent) {
            return;
        }

        composerContent.hidden = !isOpen;

        composerToggle.setAttribute(
            "aria-expanded",
            isOpen ? "true" : "false"
        );

        if (composerIcon) {
            composerIcon.setAttribute(
                "data-lucide",
                isOpen ? "chevron-down" : "chevron-up"
            );
        }

        if (isOpen && input) {
            input.focus();
        }

        refreshIcons();
    }

    function showError(message) {
        if (!errorBox) {
            return;
        }

        errorBox.textContent = message;
        errorBox.hidden = false;
    }

    function clearError() {
        if (!errorBox) {
            return;
        }

        errorBox.textContent = "";
        errorBox.hidden = true;
    }

    function updateRecipientPurposes() {
        panel.querySelectorAll(
            "[data-communication-recipient-row]"
        ).forEach(function (row) {
            const checkbox = row.querySelector(
                "[data-communication-recipient-checkbox]"
            );
            const purpose = row.querySelector(
                "[data-communication-recipient-purpose]"
            );

            if (checkbox && purpose) {
                purpose.disabled = !checkbox.checked;
            }
        });
    }

    function renderSelectedFiles() {
        if (!selectedFiles || !fileInput) {
            return;
        }

        const files = Array.from(fileInput.files || []);

        if (!files.length) {
            selectedFiles.innerHTML = "";
            selectedFiles.hidden = true;
            return;
        }

        selectedFiles.innerHTML = files.map(
            function (file) {
                return (
                    "<div>"
                    + file.name
                    + "</div>"
                );
            }
        ).join("");

        selectedFiles.hidden = false;
    }

    async function markMessagesRead() {
        const readUrl = (
            panel.dataset.communicationReadUrl
            || ""
        );

        if (!readUrl) {
            return;
        }

        const csrfToken = panel.querySelector(
            "[name='csrfmiddlewaretoken']"
        );

        if (!csrfToken) {
            return;
        }

        try {
            const response = await fetch(
                readUrl,
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRFToken": csrfToken.value,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                }
            );

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            if (
                data.ok
                && data.marked_read > 0
            ) {
                const badge = document.querySelector(
                    "[data-communication-unread-badge]"
                );

                if (badge) {
                    badge.remove();
                }
            }
        } catch {
            /* Le marquage en lecture ne bloque pas le volet. */
        }
    }

    function appendMessage(html) {
        if (!thread) {
            return;
        }

        const empty = thread.querySelector(
            "[data-communication-empty]"
        );

        if (empty) {
            empty.remove();
        }

        thread.insertAdjacentHTML(
            "beforeend",
            html
        );

        scrollToBottom();
        refreshIcons();
    }

    toggle.addEventListener(
        "click",
        function () {
            const isOpen = (
                panel.getAttribute("aria-hidden")
                === "false"
            );

            setOpen(!isOpen);
        }
    );

    if (closeButton) {
        closeButton.addEventListener(
            "click",
            function () {
                if (!isPinned()) {
                    setOpen(false);
                }
            }
        );
    }

    if (pinButton) {
        pinButton.addEventListener(
            "click",
            function () {
                setPinned(
                    !isPinned(),
                    true
                );
            }
        );
    }

    if (composerToggle) {
        composerToggle.addEventListener(
            "click",
            function () {
                const isOpen = (
                    composerToggle.getAttribute(
                        "aria-expanded"
                    )
                    === "true"
                );

                setComposerOpen(!isOpen);
            }
        );
    }

    panel.querySelectorAll(
        "[data-communication-recipient-checkbox]"
    ).forEach(function (checkbox) {
        checkbox.addEventListener(
            "change",
            updateRecipientPurposes
        );
    });

    if (fileButton && fileInput) {
        fileButton.addEventListener(
            "click",
            function () {
                fileInput.click();
            }
        );
    }

    if (fileInput) {
        fileInput.addEventListener(
            "change",
            renderSelectedFiles
        );
    }

    if (form) {
        form.addEventListener(
            "submit",
            async function (event) {
                event.preventDefault();

                clearError();

                if (submitButton) {
                    submitButton.disabled = true;
                }

                try {
                    const response = await fetch(
                        form.action,
                        {
                            method: "POST",
                            body: new FormData(form),
                            credentials: "same-origin",
                            headers: {
                                "X-Requested-With": (
                                    "XMLHttpRequest"
                                ),
                            },
                        }
                    );

                    const data = await response.json();

                    if (
                        !response.ok
                        || !data.ok
                    ) {
                        showError(
                            data.error
                            || "Le message n'a pas pu être envoyé."
                        );
                        return;
                    }

                    appendMessage(
                        data.message.html
                    );

                    form.reset();
                    renderSelectedFiles();
                    updateRecipientPurposes();
                    setComposerOpen(false);

                    if (subject) {
                        subject.value = "";
                    }
                } catch {
                    showError(
                        "Le message n'a pas pu être envoyé."
                    );
                } finally {
                    if (submitButton) {
                        submitButton.disabled = false;
                    }
                }
            }
        );
    }

    desktopMedia.addEventListener(
        "change",
        function () {
            if (!desktopMedia.matches) {
                setPinned(false, false);
            }
        }
    );

    const storedPinned = (
        localStorage.getItem(pinnedStorageKey)
        === "true"
    );

    updateRecipientPurposes();
    setComposerOpen(false);
    setPinned(storedPinned, false);
})();