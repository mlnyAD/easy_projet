

"use strict";

(function () {
    const dialog = document.querySelector(
        "[data-catalog-increment-dialog]"
    );

    if (!dialog) {
        return;
    }

    const labelInput = dialog.querySelector(
        "[data-catalog-dialog-label]"
    );
    const submitButton = dialog.querySelector(
        "[data-catalog-dialog-submit]"
    );
    const catalogCodeElement = dialog.querySelector(
        "[data-catalog-dialog-code]"
    );
    const errorElement = dialog.querySelector(
        "[data-catalog-dialog-error]"
    );

    const createUrl = dialog.dataset.createUrl;

    let sourceFieldId = null;
    let sourceButton = null;
    let catalogCode = null;
    let isSubmitting = false;

    function getCsrfToken() {
        const tokenInput = document.querySelector(
            '[name="csrfmiddlewaretoken"]'
        );

        return tokenInput ? tokenInput.value : "";
    }

    function clearError() {
        errorElement.textContent = "";
        errorElement.classList.add("hidden");
    }

    function showError(message) {
        errorElement.textContent = message;
        errorElement.classList.remove("hidden");
    }

    function updateSubmitState() {
        submitButton.disabled = (
            isSubmitting
            || !labelInput.value.trim()
        );
    }

    function openDialog(button) {
        catalogCode = button.dataset.catalogCode || "";
        sourceFieldId = button.dataset.targetField || "";
        sourceButton = button;

        catalogCodeElement.textContent = catalogCode;
        labelInput.value = "";

        clearError();

        isSubmitting = false;
        updateSubmitState();

        dialog.classList.remove("hidden");
        dialog.classList.add("flex");
        dialog.setAttribute("aria-hidden", "false");

        document.body.classList.add("overflow-hidden");

        window.setTimeout(function () {
            labelInput.focus();
        }, 0);
    }

    function closeDialog(options = {}) {
        const restoreFocus = options.restoreFocus !== false;

        dialog.classList.add("hidden");
        dialog.classList.remove("flex");
        dialog.setAttribute("aria-hidden", "true");

        document.body.classList.remove("overflow-hidden");

        labelInput.value = "";
        clearError();

        isSubmitting = false;
        submitButton.textContent = "Créer";
        updateSubmitState();

        if (restoreFocus && sourceButton) {
            sourceButton.focus();
        }

        catalogCode = null;
        sourceFieldId = null;
        sourceButton = null;
    }

    function appendAndSelectValue(value) {
        const select = document.getElementById(
            sourceFieldId
        );

        if (!select) {
            throw new Error(
                "Le champ de sélection cible est introuvable."
            );
        }

        const existingOption = Array.from(
            select.options
        ).find(function (option) {
            return option.value === value.id;
        });

        if (existingOption) {
            existingOption.selected = true;
        } else {
            select.add(
                new Option(
                    value.label,
                    value.id,
                    true,
                    true
                )
            );
        }

        select.dispatchEvent(
            new Event("change", {
                bubbles: true,
            })
        );

        return select;
    }

    async function readJsonResponse(response) {
        const contentType = response.headers.get(
            "content-type"
        ) || "";

        if (!contentType.includes("application/json")) {
            throw new Error(
                "Le serveur a retourné une réponse inattendue."
            );
        }

        return response.json();
    }

    async function createValue() {
        const label = labelInput.value.trim();

        if (
            !label
            || !catalogCode
            || isSubmitting
        ) {
            return;
        }

        clearError();

        isSubmitting = true;
        submitButton.textContent = "Création…";
        updateSubmitState();

        try {
            const response = await fetch(
                createUrl,
                {
                    method: "POST",
                    mode: "same-origin",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify({
                        catalog_code: catalogCode,
                        label: label,
                    }),
                }
            );

            const payload = await readJsonResponse(
                response
            );

            if (!response.ok || !payload.success) {
                throw new Error(
                    payload.error
                    || "La création a échoué."
                );
            }

            const select = appendAndSelectValue(
                payload.value
            );

            closeDialog({
                restoreFocus: false,
            });

            select.focus();
        } catch (error) {
            showError(
                error instanceof Error
                    ? error.message
                    : "Une erreur inattendue est survenue."
            );
        } finally {
            isSubmitting = false;
            submitButton.textContent = "Créer";
            updateSubmitState();
        }
    }

    document.addEventListener(
        "click",
        function (event) {
            const target = event.target;

            if (!(target instanceof Element)) {
                return;
            }

            const openButton = target.closest(
                "[data-catalog-increment-button]"
            );

            if (openButton) {
                openDialog(openButton);
                return;
            }

            const closeButton = target.closest(
                "[data-catalog-dialog-close]"
            );

            if (closeButton) {
                closeDialog();
            }
        }
    );

    labelInput.addEventListener(
        "input",
        function () {
            clearError();
            updateSubmitState();
        }
    );

    labelInput.addEventListener(
        "keydown",
        function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                createValue();
            }
        }
    );

    submitButton.addEventListener(
        "click",
        createValue
    );

    dialog.addEventListener(
        "click",
        function (event) {
            if (event.target === dialog) {
                closeDialog();
            }
        }
    );

    document.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key === "Escape"
                && dialog.getAttribute("aria-hidden")
                    === "false"
            ) {
                closeDialog();
            }
        }
    );
})();