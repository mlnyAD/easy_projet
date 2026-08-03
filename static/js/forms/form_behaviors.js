

"use strict";

/**
 * Comportements génériques des champs de formulaire Easy Projet.
 *
 * Les transformations JavaScript améliorent uniquement le confort de saisie.
 * La normalisation et la validation définitives restent effectuées côté serveur.
 */

(function () {
    /**
     * Supprime les espaces placés au début et à la fin d'une valeur.
     */
    function trimValue(element) {
        element.value = element.value.trim();
    }

    /**
     * Convertit une valeur en majuscules.
     */
    function uppercaseValue(element) {
        element.value = element.value.toUpperCase();
    }

    /**
     * Convertit une valeur en minuscules.
     */
    function lowercaseValue(element) {
        element.value = element.value.toLowerCase();
    }

    /**
     * Formate un numéro français de dix chiffres par groupes de deux.
     *
     * Exemples :
     *   0612345678      -> 06 12 34 56 78
     *   06-12.34/56 78 -> 06 12 34 56 78
     *
     * Les numéros commençant par « + » sont conservés dans une forme simple,
     * sans appliquer le regroupement français.
     */
    function formatPhoneValue(element) {
        const rawValue = element.value.trim();

        if (!rawValue) {
            return;
        }

        const hasInternationalPrefix = rawValue.startsWith("+");
        const digits = rawValue.replace(/\D/g, "");

        if (hasInternationalPrefix) {
            element.value = `+${digits.slice(0, 15)}`;
            return;
        }

        const limitedDigits = digits.slice(0, 10);
        const groups = limitedDigits.match(/.{1,2}/g);

        element.value = groups ? groups.join(" ") : "";
    }

    /**
     * Initialise les comportements d'un champ.
     */
    function initializeField(element) {
        if (element.dataset.behaviorsInitialized === "true") {
            return;
        }

        if (element.hasAttribute("data-uppercase")) {
            element.addEventListener("input", function () {
                uppercaseValue(element);
            });
        }

        if (element.hasAttribute("data-lowercase")) {
            element.addEventListener("input", function () {
                lowercaseValue(element);
            });
        }

        if (element.hasAttribute("data-phone")) {
            element.addEventListener("input", function () {
                formatPhoneValue(element);
            });

            formatPhoneValue(element);
        }

        if (element.hasAttribute("data-trim")) {
            element.addEventListener("blur", function () {
                trimValue(element);
            });
        }

        element.dataset.behaviorsInitialized = "true";
    }

    /**
     * Met à jour le texte associé à une case à cocher.
     */
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

        status.textContent = checkbox.checked
            ? status.dataset.checkedLabel || "Oui"
            : status.dataset.uncheckedLabel || "Non";
    }

    /**
     * Initialise l'affichage des booléens.
     */
    function initializeCheckboxFields(root = document) {
        root.querySelectorAll(
            "[data-checkbox-field]"
        ).forEach(function (container) {
            updateCheckboxStatus(container);
        });
    }

    /**
     * Met à jour le libellé correspondant à l'état d'une case à cocher.
     */
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

        const checkedLabel =
            status.dataset.checkedLabel || "Oui";
        const uncheckedLabel =
            status.dataset.uncheckedLabel || "Non";

        status.textContent = checkbox.checked
            ? checkedLabel
            : uncheckedLabel;
    }

    /**
     * Initialise tous les comportements déclaratifs des formulaires.
     */
    function initializeFormBehaviors(root = document) {
        const selector = [
            "[data-uppercase]",
            "[data-lowercase]",
            "[data-trim]",
            "[data-phone]",
        ].join(", ");

        root.querySelectorAll(selector).forEach(initializeField);

        initializeCheckboxFields(root);
    }

    /**
     * Initialise tous les champs déclarant un comportement.
     */
    function initializeFormBehaviors(root = document) {
        const selector = [
            "[data-uppercase]",
            "[data-lowercase]",
            "[data-trim]",
            "[data-phone]",
        ].join(", ");

        root.querySelectorAll(selector).forEach(initializeField);
    }

    document.addEventListener("change", function (event) {
        if (
            !event.target.matches(
                '[data-checkbox-field] input[type="checkbox"]'
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
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            initializeFormBehaviors();
        });
    } else {
        initializeFormBehaviors();
    }

    window.EasyProjetFormBehaviors = {
        initialize: initializeFormBehaviors,
    };
})();