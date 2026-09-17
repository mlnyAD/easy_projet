

"use strict";

/**
 * Comportements génériques des champs de formulaire
 * Easy Projet.
 *
 * Les transformations JavaScript améliorent uniquement
 * le confort de saisie. La normalisation et la validation
 * définitives restent effectuées côté serveur.
 */

(function () {

    function trimValue(element) {
        element.value = element.value.trim();
    }

    function uppercaseValue(element) {
        element.value = element.value.toUpperCase();
    }

    function lowercaseValue(element) {
        element.value = element.value.toLowerCase();
    }

    /**
     * Formate un numéro français de dix chiffres par
     * groupes de deux.
     */
    function formatPhoneValue(element) {
        const rawValue = element.value.trim();

        if (!rawValue) {
            return;
        }

        const hasInternationalPrefix = (
            rawValue.startsWith("+")
        );

        const digits = rawValue.replace(
            /\D/g,
            ""
        );

        if (hasInternationalPrefix) {
            element.value = (
                `+${digits.slice(0, 15)}`
            );
            return;
        }

        const limitedDigits = digits.slice(0, 10);

        const groups = limitedDigits.match(
            /.{1,2}/g
        );

        element.value = groups
            ? groups.join(" ")
            : "";
    }

    /**
     * Formate un SIRET français :
     *
     * 12345678900012 -> 123 456 789 00012
     */
    function formatSiretValue(element) {
        const digits = element.value
            .replace(
                /\D/g,
                ""
            )
            .slice(0, 14);

        const groups = [
            digits.slice(0, 3),
            digits.slice(3, 6),
            digits.slice(6, 9),
            digits.slice(9, 14),
        ];

        element.value = groups
            .filter(
                (group) => group.length > 0
            )
            .join(" ");
    }

    function initializeField(element) {
        if (
            element.dataset.behaviorsInitialized
            === "true"
        ) {
            return;
        }

        if (element.hasAttribute("data-uppercase")) {
            element.addEventListener(
                "input",
                function () {
                    uppercaseValue(element);
                }
            );
        }

        if (element.hasAttribute("data-lowercase")) {
            element.addEventListener(
                "input",
                function () {
                    lowercaseValue(element);
                }
            );
        }

        if (element.hasAttribute("data-phone")) {
            element.addEventListener(
                "input",
                function () {
                    formatPhoneValue(element);
                }
            );

            formatPhoneValue(element);
        }

        if (element.hasAttribute("data-siret")) {
            element.addEventListener(
                "input",
                function () {
                    formatSiretValue(element);
                }
            );

            formatSiretValue(element);
        }

        if (element.hasAttribute("data-trim")) {
            element.addEventListener(
                "blur",
                function () {
                    trimValue(element);
                }
            );
        }

        element.dataset.behaviorsInitialized = "true";
    }

    function updateCheckboxStatus(container) {
        const checkbox = container.querySelector(
            'input[type="checkbox"]'
        );

        const status = container.querySelector(
            "[data-checkbox-status]"
        );

        if (!checkbox || !status) {
            return;
        }

        const checkedLabel = (
            status.dataset.checkedLabel
            || "Oui"
        );

        const uncheckedLabel = (
            status.dataset.uncheckedLabel
            || "Non"
        );

        status.textContent = checkbox.checked
            ? checkedLabel
            : uncheckedLabel;
    }

    function initializeCheckboxFields(root = document) {
        root.querySelectorAll(
            "[data-checkbox-field]"
        ).forEach(function (container) {
            updateCheckboxStatus(container);
        });
    }

    function initializeFormBehaviors(root = document) {
        const selector = [
            "[data-uppercase]",
            "[data-lowercase]",
            "[data-trim]",
            "[data-phone]",
            "[data-siret]",
        ].join(", ");

        root.querySelectorAll(selector).forEach(
            initializeField
        );

        initializeCheckboxFields(root);
    }

    document.addEventListener(
        "change",
        function (event) {
            if (
                !event.target.matches(
                    "[data-checkbox-field] "
                    + 'input[type="checkbox"]'
                )
            ) {
                return;
            }

            const container = event.target.closest(
                "[data-checkbox-field]"
            );

            if (container) {
                updateCheckboxStatus(container);
            }
        }
    );

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            function () {
                initializeFormBehaviors();
            }
        );
    } else {
        initializeFormBehaviors();
    }

    window.EasyProjetFormBehaviors = {
        initialize: initializeFormBehaviors,
    };

})();