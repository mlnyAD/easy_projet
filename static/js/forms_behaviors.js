

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