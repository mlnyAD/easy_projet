

"use strict";

/**
 * Gestion générique des collections de formulaires Easy Projet.
 *
 * Responsabilités :
 * - ajouter une ligne à partir de empty_form ;
 * - mettre à jour TOTAL_FORMS ;
 * - gérer la suppression d'une ligne ;
 * - préserver le fonctionnement natif des formsets Django.
 *
 * Ce composant ne contient aucune logique métier.
 */

(function () {
    const COLLECTION_SELECTOR = "[data-ep-form-collection]";
    const BODY_SELECTOR = "[data-ep-form-collection-body]";
    const EMPTY_FORM_SELECTOR = "[data-ep-empty-form]";
    const ADD_BUTTON_SELECTOR = "[data-ep-add-row]";
    const DELETE_BUTTON_SELECTOR = "[data-ep-delete-row]";
    const ROW_SELECTOR = "[data-ep-form-row]";

    const FORM_INDEX_PLACEHOLDER = "__prefix__";

    function getCollectionName(collection) {
        return collection.dataset.epFormCollection;
    }

    function getManagementInput(collection, name) {
        const collectionName = getCollectionName(collection);

        return collection.querySelector(
            `input[name="${collectionName}-${name}"]`
        );
    }

    function getTotalFormsInput(collection) {
        return getManagementInput(
            collection,
            "TOTAL_FORMS"
        );
    }

    function getFormCount(collection) {
        const totalForms = getTotalFormsInput(collection);

        if (!totalForms) {
            throw new Error(
                "Le champ TOTAL_FORMS du formset est introuvable."
            );
        }

        return Number.parseInt(
            totalForms.value,
            10
        );
    }

    function setFormCount(collection, count) {
        const totalForms = getTotalFormsInput(collection);

        if (!totalForms) {
            throw new Error(
                "Le champ TOTAL_FORMS du formset est introuvable."
            );
        }

        totalForms.value = String(count);
    }

    function createRow(collection) {
        const template = collection.querySelector(
            EMPTY_FORM_SELECTOR
        );

        if (!template) {
            throw new Error(
                "Le modèle de ligne du formset est introuvable."
            );
        }

        const formIndex = getFormCount(collection);

        const html = template.innerHTML.replaceAll(
            FORM_INDEX_PLACEHOLDER,
            String(formIndex)
        );

        const container = document.createElement("tbody");
        container.innerHTML = html.trim();

        const row = container.firstElementChild;

        if (!row) {
            throw new Error(
                "Impossible de construire la nouvelle ligne du formset."
            );
        }

        return row;
    }

    function addRow(collection) {
        const body = collection.querySelector(
            BODY_SELECTOR
        );

        if (!body) {
            throw new Error(
                "Le corps de la collection est introuvable."
            );
        }

        const row = createRow(collection);
        const formCount = getFormCount(collection);

        body.appendChild(row);

        setFormCount(
            collection,
            formCount + 1
        );

        refreshIcons();
    }

    function getDeleteInput(row) {
        return row.querySelector(
            'input[name$="-DELETE"]'
        );
    }

    function isInitialForm(collection, row) {
        const initialForms = getManagementInput(
            collection,
            "INITIAL_FORMS"
        );

        if (!initialForms) {
            return false;
        }

        const firstField = row.querySelector(
            "input[name], select[name], textarea[name]"
        );

        if (!firstField) {
            return false;
        }

        const collectionName = getCollectionName(
            collection
        );

        const pattern = new RegExp(
            `^${escapeRegExp(collectionName)}-(\\d+)-`
        );

        const match = firstField.name.match(
            pattern
        );

        if (!match) {
            return false;
        }

        const index = Number.parseInt(
            match[1],
            10
        );

        return index < Number.parseInt(
            initialForms.value,
            10
        );
    }

    function removeRow(collection, row) {
        const deleteInput = getDeleteInput(row);

        if (
            deleteInput
            && isInitialForm(collection, row)
        ) {
            deleteInput.checked = true;
            row.hidden = true;
            return;
        }

        /*
         * Une ligne ajoutée côté navigateur ne doit pas être
         * supprimée physiquement sans renumérotation des formulaires.
         *
         * On la conserve donc dans le formset et on utilise DELETE
         * lorsque ce champ est disponible.
         */
        if (deleteInput) {
            deleteInput.checked = true;
            row.hidden = true;
            return;
        }

        /*
         * Cas défensif : si le formset n'utilise pas can_delete,
         * la ligne est simplement masquée.
         *
         * La configuration normale d'une collection supprimable
         * doit fournir DELETE côté Django.
         */
        row.hidden = true;
    }

    function escapeRegExp(value) {
        return value.replace(
            /[.*+?^${}()|[\]\\]/g,
            "\\$&"
        );
    }

    function refreshIcons() {
        if (
            window.lucide
            && typeof window.lucide.createIcons === "function"
        ) {
            window.lucide.createIcons();
        }
    }

    function handleClick(event) {
        const addButton = event.target.closest(
            ADD_BUTTON_SELECTOR
        );

        if (addButton) {
            const collection = addButton.closest(
                COLLECTION_SELECTOR
            );

            if (collection) {
                addRow(collection);
            }

            return;
        }

        const deleteButton = event.target.closest(
            DELETE_BUTTON_SELECTOR
        );

        if (!deleteButton) {
            return;
        }

        const row = deleteButton.closest(
            ROW_SELECTOR
        );

        const collection = deleteButton.closest(
            COLLECTION_SELECTOR
        );

        if (
            !row
            || !collection
        ) {
            return;
        }

        removeRow(
            collection,
            row
        );
    }

    function initialize() {
        document.addEventListener(
            "click",
            handleClick
        );
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initialize
        );
    } else {
        initialize();
    }
})();