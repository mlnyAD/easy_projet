

"use strict";

(function () {

    const components = document.querySelectorAll(
        "[data-file-upload]"
    );

    if (!components.length) {
        return;
    }


    function getFileInput(component) {
        return component.querySelector(
            'input[type="file"]'
        );
    }


    function getClearInput(component) {
        return component.querySelector(
            "[data-file-upload-clear]"
        );
    }


    function getNameElement(component) {
        return component.querySelector(
            "[data-file-upload-name]"
        );
    }


    function getPreviewImage(component) {
        return component.querySelector(
            "[data-file-upload-preview-image]"
        );
    }


    function getIcon(component) {
        return component.querySelector(
            "[data-file-upload-icon]"
        );
    }


    function supportsPreview(component) {
        return (
            component.dataset.fileUploadPreview
            === "true"
        );
    }


    function createPreviewImage(component) {
        const current = component.querySelector(
            "[data-file-upload-current]"
        );

        if (!current) {
            return null;
        }

        const icon = getIcon(component);

        if (icon) {
            icon.remove();
        }

        const image = document.createElement(
            "img"
        );

        image.alt = "";
        image.className =
            "ep-file-upload-preview";

        image.setAttribute(
            "data-file-upload-preview-image",
            ""
        );

        current.prepend(image);

        return image;
    }


    function clearPreview(component) {
        const image = getPreviewImage(
            component
        );

        if (image) {
            const objectUrl =
                image.dataset.objectUrl;

            if (objectUrl) {
                URL.revokeObjectURL(
                    objectUrl
                );
            }

            image.removeAttribute("src");
            image.classList.add(
                "hidden"
            );
        }

        const name = getNameElement(
            component
        );

        if (name) {
            name.textContent =
                "Suppression demandée";
        }
    }


    function updatePreview(
        component,
        file
    ) {
        const name = getNameElement(
            component
        );

        if (name) {
            name.textContent = file.name;
        }

        if (
            !supportsPreview(component)
            || !file.type.startsWith("image/")
        ) {
            return;
        }

        let image = getPreviewImage(
            component
        );

        if (!image) {
            image = createPreviewImage(
                component
            );
        }

        if (!image) {
            return;
        }

        const previousObjectUrl =
            image.dataset.objectUrl;

        if (previousObjectUrl) {
            URL.revokeObjectURL(
                previousObjectUrl
            );
        }

        const objectUrl =
            URL.createObjectURL(file);

        image.src = objectUrl;
        image.dataset.objectUrl =
            objectUrl;

        image.classList.remove(
            "hidden"
        );
    }


    function bindComponent(component) {
        const fileInput = getFileInput(
            component
        );

        if (!fileInput) {
            return;
        }

        const clearInput = getClearInput(
            component
        );


        fileInput.addEventListener(
            "change",
            function () {

                const files =
                    Array.from(
                        fileInput.files || []
                    );

                if (!files.length) {
                    return;
                }

                if (clearInput) {
                    clearInput.checked =
                        false;
                }

                updatePreview(
                    component,
                    files[0]
                );
            }
        );


        if (clearInput) {
            clearInput.addEventListener(
                "change",
                function () {

                    if (!clearInput.checked) {
                        return;
                    }

                    fileInput.value = "";

                    clearPreview(
                        component
                    );
                }
            );
        }
    }


    components.forEach(
        bindComponent
    );

})();