

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

    const submitLabel = dialog.querySelector(
        "[data-catalog-dialog-submit-label]"
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


    /*
     * Retourne le jeton CSRF du formulaire courant.
     */
    function getCsrfToken() {
        const tokenInput = document.querySelector(
            '[name="csrfmiddlewaretoken"]'
        );

        return tokenInput
            ? tokenInput.value
            : "";
    }


    /*
     * Masque et réinitialise le message d'erreur.
     */
    function clearError() {
        errorElement.textContent = "";
        errorElement.hidden = true;
    }


    /*
     * Affiche un message d'erreur dans le dialogue.
     */
    function showError(message) {
        errorElement.textContent = message;
        errorElement.hidden = false;
    }


    /*
     * Active ou désactive le bouton de création.
     */
    function updateSubmitState() {
        submitButton.disabled = (
            isSubmitting
            || !labelInput.value.trim()
        );
    }


    /*
     * Modifie uniquement le libellé du bouton.
     *
     * La structure HTML du composant ep-button reste intacte.
     */
    function setSubmitLabel(label) {
        if (submitLabel) {
            submitLabel.textContent = label;
        }
    }


    /*
     * Ouvre le dialogue pour le catalogue demandé.
     */
    function openDialog(button) {
        catalogCode = (
            button.dataset.catalogCode
            || ""
        );

        sourceFieldId = (
            button.dataset.targetField
            || ""
        );

        sourceButton = button;

        catalogCodeElement.textContent = (
            catalogCode
        );

        labelInput.value = "";

        clearError();

        isSubmitting = false;

        setSubmitLabel("Créer");
        updateSubmitState();

        dialog.classList.add(
            "is-open"
        );

        dialog.setAttribute(
            "aria-hidden",
            "false"
        );

        document.body.classList.add(
            "ep-dialog-open"
        );

        window.setTimeout(
            function () {
                labelInput.focus();
            },
            0
        );
    }


    /*
     * Ferme le dialogue et réinitialise son état.
     */
    function closeDialog(
        options = {}
    ) {
        const restoreFocus = (
            options.restoreFocus !== false
        );

        dialog.classList.remove(
            "is-open"
        );

        dialog.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.classList.remove(
            "ep-dialog-open"
        );

        labelInput.value = "";

        clearError();

        isSubmitting = false;

        setSubmitLabel("Créer");
        updateSubmitState();

        if (
            restoreFocus
            && sourceButton
        ) {
            sourceButton.focus();
        }

        catalogCode = null;
        sourceFieldId = null;
        sourceButton = null;
    }


    /*
     * Ajoute la nouvelle valeur au select d'origine
     * puis la sélectionne.
     */
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
        ).find(
            function (option) {
                return (
                    option.value
                    === value.id
                );
            }
        );

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
            new Event(
                "change",
                {
                    bubbles: true,
                }
            )
        );

        return select;
    }


    /*
     * Vérifie que la réponse serveur contient du JSON.
     */
    async function readJsonResponse(
        response
    ) {
        const contentType = (
            response.headers.get(
                "content-type"
            )
            || ""
        );

        if (
            !contentType.includes(
                "application/json"
            )
        ) {
            throw new Error(
                "Le serveur a retourné une réponse inattendue."
            );
        }

        return response.json();
    }


    /*
     * Crée une nouvelle valeur de catalogue.
     */
    async function createValue() {
        const label = (
            labelInput.value.trim()
        );

        if (
            !label
            || !catalogCode
            || isSubmitting
        ) {
            return;
        }

        clearError();

        isSubmitting = true;

        setSubmitLabel(
            "Création…"
        );

        updateSubmitState();

        try {
            const response = await fetch(
                createUrl,
                {
                    method: "POST",
                    mode: "same-origin",
                    credentials: "same-origin",

                    headers: {
                        "Content-Type": (
                            "application/json"
                        ),
                        "X-CSRFToken": (
                            getCsrfToken()
                        ),
                    },

                    body: JSON.stringify({
                        catalog_code: (
                            catalogCode
                        ),
                        label: label,
                    }),
                }
            );

            const payload = (
                await readJsonResponse(
                    response
                )
            );

            if (
                !response.ok
                || !payload.success
            ) {
                throw new Error(
                    payload.error
                    || "La création a échoué."
                );
            }

            const select = (
                appendAndSelectValue(
                    payload.value
                )
            );

            closeDialog({
                restoreFocus: false,
            });

            select.focus();

        } catch (error) {
            showError(
                error instanceof Error
                    ? error.message
                    : (
                        "Une erreur inattendue "
                        + "est survenue."
                    )
            );

        } finally {
            isSubmitting = false;

            setSubmitLabel(
                "Créer"
            );

            updateSubmitState();
        }
    }


    /*
     * Ouverture et fermeture depuis les boutons
     * portant les attributs data-* EDF.
     */
    document.addEventListener(
        "click",
        function (event) {
            const target = event.target;

            if (
                !(target instanceof Element)
            ) {
                return;
            }

            const openButton = (
                target.closest(
                    "[data-catalog-increment-button]"
                )
            );

            if (openButton) {
                openDialog(
                    openButton
                );
                return;
            }

            const closeButton = (
                target.closest(
                    "[data-catalog-dialog-close]"
                )
            );

            if (closeButton) {
                closeDialog();
            }
        }
    );


    /*
     * Actualisation de l'état du bouton
     * pendant la saisie.
     */
    labelInput.addEventListener(
        "input",
        function () {
            clearError();
            updateSubmitState();
        }
    );


    /*
     * Entrée valide directement la création.
     */
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


    /*
     * Un clic sur l'overlay ferme le dialogue.
     */
    dialog.addEventListener(
        "click",
        function (event) {
            if (event.target === dialog) {
                closeDialog();
            }
        }
    );


    /*
     * La touche Échap ferme le dialogue ouvert.
     */
    document.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key === "Escape"
                && dialog.getAttribute(
                    "aria-hidden"
                ) === "false"
            ) {
                closeDialog();
            }
        }
    );
})();