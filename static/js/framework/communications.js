

"use strict";


(function () {

    const PANEL_SELECTOR = (
        "[data-communication-panel]"
    );

    const TOGGLE_SELECTOR = (
        "[data-communication-toggle]"
    );

    const CLOSE_SELECTOR = (
        "[data-communication-close]"
    );

    const PIN_SELECTOR = (
        "[data-communication-pin]"
    );

    const PIN_ICON_SELECTOR = (
        "[data-communication-pin-icon]"
    );

    const THREAD_SELECTOR = (
        "[data-communication-thread]"
    );

    const FORM_SELECTOR = (
        "[data-communication-form]"
    );

    const INPUT_SELECTOR = (
        "[data-communication-input]"
    );

    const SUBJECT_SELECTOR = (
        "[data-communication-subject]"
    );

    const RECIPIENT_CHECKBOX_SELECTOR = (
        "[data-communication-recipient-checkbox]"
    );

    const RECIPIENT_ROW_SELECTOR = (
        "[data-communication-recipient-row]"
    );

    const RECIPIENT_PURPOSE_SELECTOR = (
        "[data-communication-recipient-purpose]"
    );

    const SUBMIT_SELECTOR = (
        "[data-communication-submit]"
    );

    const ERROR_SELECTOR = (
        "[data-communication-error]"
    );

    const EMPTY_SELECTOR = (
        "[data-communication-empty]"
    );

    const FILE_INPUT_SELECTOR = (
        "[data-communication-file-input]"
    );

    const FILE_BUTTON_SELECTOR = (
        "[data-communication-file-button]"
    );

    const SELECTED_FILES_SELECTOR = (
        "[data-communication-selected-files]"
    );

    const COMPOSER_TOGGLE_SELECTOR = (
        "[data-communication-composer-toggle]"
    );

    const COMPOSER_CONTENT_SELECTOR = (
        "[data-communication-composer-content]"
    );

    const COMPOSER_TOGGLE_ICON_SELECTOR = (
        "[data-communication-composer-toggle-icon]"
    );


    const PINNED_STORAGE_KEY = (
        "easy-projet-communication-pinned"
    );

    const PINNED_MEDIA_QUERY = (
        "(min-width: 1024px)"
    );


    function initializeCommunicationPanel() {

        const panel = document.querySelector(
            PANEL_SELECTOR
        );

        const readUrl = (
            panel.dataset.communicationReadUrl
            || ""
        );

        const toggle = document.querySelector(
            TOGGLE_SELECTOR
        );

        if (!panel || !toggle) {
            return;
        }

        if (
            toggle.dataset.communicationInitialized
            === "true"
        ) {
            return;
        }

        toggle.dataset.communicationInitialized = (
            "true"
        );


        const appMain = panel.closest(
            ".ep-app-main"
        );

        const thread = panel.querySelector(
            THREAD_SELECTOR
        );

        const form = panel.querySelector(
            FORM_SELECTOR
        );

        const input = panel.querySelector(
            INPUT_SELECTOR
        );

        const subjectInput = panel.querySelector(
            SUBJECT_SELECTOR
        );

        const recipientCheckboxes = (
            panel.querySelectorAll(
                RECIPIENT_CHECKBOX_SELECTOR
            )
        );

        const submitButton = panel.querySelector(
            SUBMIT_SELECTOR
        );

        const errorBox = panel.querySelector(
            ERROR_SELECTOR
        );

        const fileInput = panel.querySelector(
            FILE_INPUT_SELECTOR
        );

        const fileButton = panel.querySelector(
            FILE_BUTTON_SELECTOR
        );

        const selectedFiles = panel.querySelector(
            SELECTED_FILES_SELECTOR
        );

        const pinButton = panel.querySelector(
            PIN_SELECTOR
        );

        const composerToggle = panel.querySelector(
            COMPOSER_TOGGLE_SELECTOR
        );

        const composerContent = panel.querySelector(
            COMPOSER_CONTENT_SELECTOR
        );

        const composerToggleIcon = panel.querySelector(
            COMPOSER_TOGGLE_ICON_SELECTOR
        );

        const mediaQuery = window.matchMedia(
            PINNED_MEDIA_QUERY
        );


        let pendingFiles = [];


        function refreshIcons() {

            if (
                window.lucide
                && typeof (
                    window.lucide.createIcons
                ) === "function"
            ) {
                window.lucide.createIcons();
            }
        }


        function scrollThreadToBottom() {

            if (!thread) {
                return;
            }

            thread.scrollTop = (
                thread.scrollHeight
            );
        }

    async function markMessagesRead() {

        if (!readUrl) {
            return;
        }

        const badge = document.querySelector(
            "[data-communication-unread-badge]"
        );

        if (!badge) {
            return;
        }

        const csrfToken = document.querySelector(
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
                        "X-CSRFToken": (
                            csrfToken.value
                        ),
                        "X-Requested-With": (
                            "XMLHttpRequest"
                        ),
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
                badge.remove();
            }

        } catch {

            /*
            * L'échec du marquage en lecture
            * ne doit jamais bloquer le panneau.
            */
        }
    }       

        function isPinned() {

            return panel.classList.contains(
                "ep-communication-panel-pinned"
            );
        }


        function setOpen(isOpen) {

            if (
                isPinned()
                && mediaQuery.matches
            ) {
                isOpen = true;
            }

            panel.classList.toggle(
                "ep-communication-panel-open",
                isOpen
            );

            panel.setAttribute(
                "aria-hidden",
                isOpen
                    ? "false"
                    : "true"
            );

            toggle.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );

            if (isOpen) {

                scrollThreadToBottom();
                
                markMessagesRead();
            }
        }


        function setPinned(
            pinned,
            {
                persist = true,
            } = {}
        ) {

            if (!mediaQuery.matches) {
                pinned = false;
            }

            const pinIcon = panel.querySelector(
                PIN_ICON_SELECTOR
            );

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
                    pinned
                        ? "true"
                        : "false"
                );

                pinButton.setAttribute(
                    "aria-label",
                    pinned
                        ? "Désépingler le volet"
                        : "Épingler le volet"
                );

                pinButton.title = (
                    pinned
                        ? "Désépingler le volet"
                        : "Épingler le volet"
                );
            }

            if (pinIcon) {

                pinIcon.setAttribute(
                    "data-lucide",
                    pinned
                        ? "pin"
                        : "pin-off"
                );
            }

            if (persist) {

                localStorage.setItem(
                    PINNED_STORAGE_KEY,
                    pinned
                        ? "true"
                        : "false"
                );
            }

            if (pinned) {
                setOpen(true);
            }

            refreshIcons();
        }


        function restorePinnedState() {

            const storedValue = (
                localStorage.getItem(
                    PINNED_STORAGE_KEY
                )
            );

            setPinned(
                storedValue === "true",
                {
                    persist: false,
                }
            );
        }


        function setComposerOpen(
            isOpen
        ) {

            if (
                !composerContent
                || !composerToggle
            ) {
                return;
            }

            composerContent.hidden = (
                !isOpen
            );

            composerToggle.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );

            if (composerToggleIcon) {

                composerToggleIcon.setAttribute(
                    "data-lucide",
                    isOpen
                        ? "chevron-down"
                        : "chevron-up"
                );
            }

            refreshIcons();

            if (
                isOpen
                && input
            ) {
                input.focus();
            }
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


        function updateRecipientRow(
            checkbox
        ) {

            const row = checkbox.closest(
                RECIPIENT_ROW_SELECTOR
            );

            if (!row) {
                return;
            }

            const purposeSelect = row.querySelector(
                RECIPIENT_PURPOSE_SELECTOR
            );

            row.classList.toggle(
                "ep-communication-recipient-row-selected",
                checkbox.checked
            );

            if (purposeSelect) {

                purposeSelect.disabled = (
                    !checkbox.checked
                );
            }
        }


        function hasSelectedRecipient() {

            for (
                const checkbox
                of recipientCheckboxes
            ) {

                if (checkbox.checked) {
                    return true;
                }
            }

            return false;
        }


        function setSubmitting(
            isSubmitting
        ) {

            if (submitButton) {

                submitButton.disabled = (
                    isSubmitting
                );
            }

            if (input) {

                input.disabled = (
                    isSubmitting
                );
            }

            if (subjectInput) {

                subjectInput.disabled = (
                    isSubmitting
                );
            }

            if (fileButton) {

                fileButton.disabled = (
                    isSubmitting
                );
            }

            for (
                const checkbox
                of recipientCheckboxes
            ) {

                checkbox.disabled = (
                    isSubmitting
                );

                const row = checkbox.closest(
                    RECIPIENT_ROW_SELECTOR
                );

                const purposeSelect = (
                    row
                        ? row.querySelector(
                            RECIPIENT_PURPOSE_SELECTOR
                        )
                        : null
                );

                if (purposeSelect) {

                    purposeSelect.disabled = (
                        isSubmitting
                        || !checkbox.checked
                    );
                }
            }
        }


        function getFileKey(file) {

            return [
                file.name,
                file.size,
                file.lastModified,
            ].join("::");
        }


        function addPendingFiles(files) {

            const existingKeys = new Set(
                pendingFiles.map(
                    getFileKey
                )
            );

            for (const file of files) {

                const key = getFileKey(
                    file
                );

                if (existingKeys.has(key)) {
                    continue;
                }

                pendingFiles.push(
                    file
                );

                existingKeys.add(
                    key
                );
            }
        }


        function removePendingFile(index) {

            pendingFiles.splice(
                index,
                1
            );

            syncFileInput();
            renderSelectedFiles();
        }


        function syncFileInput() {

            if (!fileInput) {
                return;
            }

            const transfer = (
                new DataTransfer()
            );

            for (const file of pendingFiles) {

                transfer.items.add(
                    file
                );
            }

            fileInput.files = (
                transfer.files
            );
        }


        function renderSelectedFiles() {

            if (!selectedFiles) {
                return;
            }

            selectedFiles.replaceChildren();

            if (!pendingFiles.length) {

                selectedFiles.hidden = true;

                return;
            }

            pendingFiles.forEach(
                function (
                    file,
                    index
                ) {

                    const item = (
                        document.createElement(
                            "div"
                        )
                    );

                    item.className = (
                        "ep-communication-selected-file"
                    );


                    const icon = (
                        document.createElement(
                            "i"
                        )
                    );

                    icon.setAttribute(
                        "data-lucide",
                        "paperclip"
                    );

                    icon.className = (
                        "ep-communication-attachment-icon"
                    );


                    const name = (
                        document.createElement(
                            "span"
                        )
                    );

                    name.className = (
                        "ep-communication-selected-file-name"
                    );

                    name.textContent = (
                        file.name
                    );


                    const removeButton = (
                        document.createElement(
                            "button"
                        )
                    );

                    removeButton.type = "button";

                    removeButton.className = (
                        "ep-communication-selected-file-remove"
                    );

                    removeButton.title = (
                        `Retirer ${file.name}`
                    );

                    removeButton.setAttribute(
                        "aria-label",
                        `Retirer ${file.name}`
                    );


                    const removeIcon = (
                        document.createElement(
                            "i"
                        )
                    );

                    removeIcon.setAttribute(
                        "data-lucide",
                        "x"
                    );

                    removeIcon.className = (
                        "ep-communication-selected-file-remove-icon"
                    );


                    removeButton.appendChild(
                        removeIcon
                    );

                    removeButton.addEventListener(
                        "click",
                        function () {

                            removePendingFile(
                                index
                            );
                        }
                    );


                    item.appendChild(
                        icon
                    );

                    item.appendChild(
                        name
                    );

                    item.appendChild(
                        removeButton
                    );

                    selectedFiles.appendChild(
                        item
                    );
                }
            );

            selectedFiles.hidden = false;

            refreshIcons();
        }


        function handleFileSelection() {

            if (!fileInput) {
                return;
            }

            addPendingFiles(
                Array.from(
                    fileInput.files
                )
            );

            syncFileInput();
            renderSelectedFiles();
        }


        function appendMessage(
            message
        ) {

            if (!thread) {
                return;
            }

            const empty = thread.querySelector(
                EMPTY_SELECTOR
            );

            if (empty) {
                empty.remove();
            }

            const container = (
                document.createElement(
                    "div"
                )
            );

            container.innerHTML = (
                message.html.trim()
            );

            const messageElement = (
                container.firstElementChild
            );

            if (!messageElement) {
                return;
            }

            thread.appendChild(
                messageElement
            );

            refreshIcons();
            scrollThreadToBottom();
        }


        function clearFiles() {

            pendingFiles = [];

            syncFileInput();

            if (selectedFiles) {

                selectedFiles.replaceChildren();
                selectedFiles.hidden = true;
            }
        }


        function clearRecipients() {

            for (
                const checkbox
                of recipientCheckboxes
            ) {

                checkbox.checked = false;

                const row = checkbox.closest(
                    RECIPIENT_ROW_SELECTOR
                );

                const purposeSelect = (
                    row
                        ? row.querySelector(
                            RECIPIENT_PURPOSE_SELECTOR
                        )
                        : null
                );

                if (purposeSelect) {

                    purposeSelect.value = (
                        "INFORMATION"
                    );
                }

                updateRecipientRow(
                    checkbox
                );
            }
        }


        function clearComposer() {

            if (subjectInput) {

                subjectInput.value = "";
            }

            if (input) {

                input.value = "";
            }

            clearRecipients();
            clearFiles();
        }


        async function submitMessage(
            event
        ) {

            event.preventDefault();

            if (!form || !input) {
                return;
            }

            clearError();

            const body = (
                input.value.trim()
            );

            const subject = (
                subjectInput
                    ? subjectInput.value.trim()
                    : ""
            );

            if (!hasSelectedRecipient()) {

                showError(
                    "Sélectionnez au moins "
                    + "un destinataire."
                );

                return;
            }

            if (!body) {

                showError(
                    "Le message ne peut pas être vide."
                );

                input.focus();

                return;
            }


            /*
             * FormData doit être construit avant
             * la désactivation des contrôles.
             */
            const formData = (
                new FormData(
                    form
                )
            );

            formData.set(
                "body",
                body
            );

            formData.set(
                "subject",
                subject
            );


            setSubmitting(true);


            try {

                const response = await fetch(
                    form.action,
                    {
                        method: "POST",
                        body: formData,
                        credentials: "same-origin",
                        headers: {
                            "X-Requested-With": (
                                "XMLHttpRequest"
                            ),
                        },
                    }
                );

                const data = (
                    await response.json()
                );

                if (
                    !response.ok
                    || !data.ok
                ) {

                    throw new Error(
                        data.error
                        || (
                            "Le message n'a pas "
                            + "pu être envoyé."
                        )
                    );
                }


                clearComposer();

                setComposerOpen(
                    false
                );

                appendMessage(
                    data.message
                );

            } catch (error) {

                showError(
                    error.message
                    || (
                        "Le message n'a pas "
                        + "pu être envoyé."
                    )
                );

            } finally {

                setSubmitting(false);
            }
        }


        /*
         * Ouverture / fermeture du compositeur.
         */
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

                    setComposerOpen(
                        !isOpen
                    );
                }
            );
        }


        /*
         * Ouverture / fermeture du panneau.
         */
        toggle.addEventListener(
            "click",
            function () {

                if (
                    isPinned()
                    && mediaQuery.matches
                ) {
                    return;
                }

                const isOpen = (
                    panel.classList.contains(
                        "ep-communication-panel-open"
                    )
                );

                setOpen(
                    !isOpen
                );
            }
        );


        const closeButton = panel.querySelector(
            CLOSE_SELECTOR
        );

        if (closeButton) {

            closeButton.addEventListener(
                "click",
                function () {

                    if (isPinned()) {
                        setPinned(false);
                    }

                    setOpen(false);
                }
            );
        }


        if (pinButton) {

            pinButton.addEventListener(
                "click",
                function () {

                    setPinned(
                        !isPinned()
                    );
                }
            );
        }


        for (
            const checkbox
            of recipientCheckboxes
        ) {

            checkbox.addEventListener(
                "change",
                function () {

                    updateRecipientRow(
                        checkbox
                    );
                }
            );

            updateRecipientRow(
                checkbox
            );
        }


        if (
            fileButton
            && fileInput
        ) {

            fileButton.addEventListener(
                "click",
                function () {

                    fileInput.click();
                }
            );

            fileInput.addEventListener(
                "change",
                handleFileSelection
            );
        }


        if (form) {

            form.addEventListener(
                "submit",
                submitMessage
            );
        }


        document.addEventListener(
            "keydown",
            function (event) {

                if (event.key !== "Escape") {
                    return;
                }

                /*
                 * Si le compositeur est ouvert,
                 * Échap le replie en priorité.
                 */
                if (
                    composerToggle
                    && (
                        composerToggle.getAttribute(
                            "aria-expanded"
                        )
                        === "true"
                    )
                ) {

                    setComposerOpen(
                        false
                    );

                    return;
                }

                if (isPinned()) {
                    return;
                }

                if (
                    panel.classList.contains(
                        "ep-communication-panel-open"
                    )
                ) {

                    setOpen(
                        false
                    );
                }
            }
        );


        mediaQuery.addEventListener(
            "change",
            function (event) {

                if (!event.matches) {

                    panel.classList.remove(
                        "ep-communication-panel-pinned"
                    );

                    if (appMain) {

                        appMain.classList.remove(
                            "ep-app-main-communication-pinned"
                        );
                    }

                    if (pinButton) {

                        pinButton.setAttribute(
                            "aria-pressed",
                            "false"
                        );
                    }

                    setOpen(false);

                    return;
                }

                restorePinnedState();
            }
        );


        /*
         * État initial.
         */
        setComposerOpen(
            false
        );

        restorePinnedState();
    }


    if (
        document.readyState
        === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initializeCommunicationPanel,
            {
                once: true,
            }
        );

    } else {

        initializeCommunicationPanel();
    }

})();