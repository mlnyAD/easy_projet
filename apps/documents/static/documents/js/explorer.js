

document.addEventListener("DOMContentLoaded", () => {

    const folderMenu = document.getElementById(
        "folder-context-menu"
    );

    const contentMenu = document.getElementById(
        "content-context-menu"
    );

    const documentContent = document.getElementById(
        "document-content"
    );

    const dialog = document.getElementById(
        "folder-dialog"
    );

    const dialogForm = document.getElementById(
        "folder-dialog-form"
    );

    const dialogTitle = document.getElementById(
        "folder-dialog-title"
    );

    const nameInput = document.getElementById(
        "folder-dialog-name"
    );

    const parentInput = document.getElementById(
        "folder-dialog-parent-id"
    );

    const cancelButton = document.getElementById(
        "folder-dialog-cancel"
    );

    const deleteForm = document.getElementById(
        "folder-delete-form"
    );

    const contentCreateFolder =
        document.getElementById(
            "content-create-folder"
        );

    const contentImportDocument =
        document.getElementById(
            "content-import-document"
        );

    const documentRows = document.querySelectorAll(
        "[data-document-row]"
    );

    const documentMenu = document.getElementById(
        "document-context-menu"
    );

    const documentRenameDialog =
        document.getElementById(
            "document-rename-dialog"
        );

    const documentRenameForm =
        document.getElementById(
            "document-rename-form"
        );

    const documentRenameTitle =
        document.getElementById(
            "document-rename-title"
        );

    const documentRenameCancel =
        document.getElementById(
            "document-rename-cancel"
        );    

    const documentMoveDialog =
        document.getElementById(
            "document-move-dialog"
        );

    const documentMoveForm =
        document.getElementById(
            "document-move-form"
        );

    const documentMoveDestination =
        document.getElementById(
            "document-move-destination"
        );

    const documentMoveCancel =
        document.getElementById(
            "document-move-cancel"
        );

    const documentCopyDialog =
        document.getElementById(
            "document-copy-dialog"
        );

    const documentCopyForm =
        document.getElementById(
            "document-copy-form"
        );

    const documentCopyTitle =
        document.getElementById(
            "document-copy-title"
        );

    const documentCopyDestination =
        document.getElementById(
            "document-copy-destination"
        );

    const documentCopyCancel =
        document.getElementById(
            "document-copy-cancel"
        );

    const documentFavoriteLabel =
        document.querySelector(
            "[data-document-favorite-label]"
        );

    const documentFavoriteIcon =
        document.querySelector(
            "[data-document-favorite-icon]"
        );

    let selectedDocumentRow = null;


    documentRows.forEach((row) => {

        row.addEventListener(
            "click",
            () => {

                if (selectedDocumentRow) {
                    selectedDocumentRow.classList.remove(
                        "bg-axcio-surface-alt",
                        "dark:bg-axcio-surface-alt-dark"
                    );
                }

                selectedDocumentRow = row;

                selectedDocumentRow.classList.add(
                    "bg-axcio-surface-alt",
                    "dark:bg-axcio-surface-alt-dark"
                );
            }
        );


        row.addEventListener(
            "dblclick",
            () => {
                openDocument(row);
            }
        );

        row.addEventListener(
            "contextmenu",
            (event) => {

                event.preventDefault();
                event.stopPropagation();

                hideMenus();

                selectedDocumentRow = row;

                const isFavorite =
                    row.dataset.documentFavorite === "true";

                if (documentFavoriteLabel) {
                    documentFavoriteLabel.textContent =
                        isFavorite
                            ? "Retirer des favoris"
                            : "Ajouter aux favoris";
                }

                if (documentFavoriteIcon) {
                    documentFavoriteIcon.setAttribute(
                        "data-lucide",
                        isFavorite
                            ? "star-off"
                            : "star"
                    );
                }

                if (window.lucide) {
                    lucide.createIcons();
                }

                documentMenu.classList.remove(
                    "hidden"
                );

                positionMenu(
                    documentMenu,
                    event.clientX,
                    event.clientY
                );
            }
        );

    });

    documentMenu
        .querySelectorAll(
            "[data-document-action]"
        )
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    if (!selectedDocumentRow) {
                        return;
                    }

                    const action =
                        button.dataset.documentAction;

                    hideMenus();

                    if (action === "open") {
                        openDocument(
                            selectedDocumentRow
                        );
                        return;
                    }

                    if (action === "download") {

                        const downloadUrl =
                            selectedDocumentRow.dataset
                                .documentDownloadUrl;

                        if (!downloadUrl) {
                            return;
                        }

                        const link =
                            document.createElement("a");

                        link.href = downloadUrl;
                        link.download = "";

                        document.body.appendChild(link);

                        link.click();

                        link.remove();

                        return;
                    }

                    if (action === "rename") {

                        const renameUrl =
                            selectedDocumentRow.dataset
                                .documentRenameUrl;

                        const currentTitle =
                            selectedDocumentRow.dataset
                                .documentTitle;

                        if (!renameUrl) {
                            return;
                        }

                        documentRenameForm.action =
                            renameUrl;

                        documentRenameTitle.value =
                            currentTitle || "";

                        documentRenameDialog.showModal();

                        documentRenameTitle.focus();
                        documentRenameTitle.select();

                        return;
                    }

                    if (action === "move") {

                        const moveUrl =
                            selectedDocumentRow.dataset
                                .documentMoveUrl;

                        const currentFolderId =
                            selectedDocumentRow.dataset
                                .documentFolderId;

                        if (!moveUrl) {
                            return;
                        }

                        documentMoveForm.action =
                            moveUrl;

                        documentMoveDestination.value =
                            currentFolderId || "";

                        documentMoveDialog.showModal();

                        documentMoveDestination.focus();

                        return;
                    }

                if (action === "copy") {

                    const copyUrl =
                        selectedDocumentRow.dataset
                            .documentCopyUrl;

                    const currentTitle =
                        selectedDocumentRow.dataset
                            .documentTitle;

                    const currentFolderId =
                        selectedDocumentRow.dataset
                            .documentFolderId;

                    if (!copyUrl) {
                        return;
                    }

                    documentCopyForm.action =
                        copyUrl;

                    documentCopyTitle.value =
                        currentTitle || "";

                    documentCopyDestination.value =
                        currentFolderId || "";

                    documentCopyDialog.showModal();

                    documentCopyTitle.focus();
                    documentCopyTitle.select();

                    return;
                }    

                if (action === "favorite") {

                    const isFavorite =
                        selectedDocumentRow.dataset
                            .documentFavorite === "true";

                    const favoriteUrl =
                        isFavorite
                            ? selectedDocumentRow.dataset
                                .documentFavoriteRemoveUrl
                            : selectedDocumentRow.dataset
                                .documentFavoriteAddUrl;

                    if (!favoriteUrl) {
                        return;
                    }

                    const form =
                        document.createElement("form");

                    form.method = "post";
                    form.action = favoriteUrl;

                    const csrfToken =
                        document.querySelector(
                            "[name=csrfmiddlewaretoken]"
                        );

                    if (!csrfToken) {
                        return;
                    }

                    const csrfInput =
                        document.createElement("input");

                    csrfInput.type = "hidden";
                    csrfInput.name = "csrfmiddlewaretoken";
                    csrfInput.value = csrfToken.value;

                    form.appendChild(
                        csrfInput
                    );

                    document.body.appendChild(
                        form
                    );

                    form.submit();

                    return;
                }

                if (action === "delete") {

                    const deleteUrl =
                        selectedDocumentRow.dataset
                            .documentDeleteUrl;

                    const title =
                        selectedDocumentRow.dataset
                            .documentTitle;

                    if (!deleteUrl) {
                        return;
                    }

                    const confirmed =
                        window.confirm(
                            `Supprimer définitivement le document `
                            + `"${title}" et toutes ses versions ?`
                        );

                    if (!confirmed) {
                        return;
                    }

                    const form =
                        document.createElement("form");

                    form.method = "post";
                    form.action = deleteUrl;

                    const csrfToken =
                        document.querySelector(
                            "[name=csrfmiddlewaretoken]"
                        );

                    if (!csrfToken) {
                        return;
                    }

                    const csrfInput =
                        document.createElement("input");

                    csrfInput.type = "hidden";
                    csrfInput.name = "csrfmiddlewaretoken";
                    csrfInput.value = csrfToken.value;

                    form.appendChild(
                        csrfInput
                    );

                    document.body.appendChild(
                        form
                    );

                    form.submit();

                    return;
                }

                }

                
        );

    });

    let selectedFolder = null;


    // -----------------------------------------------------------------
    // Menus contextuels
    // -----------------------------------------------------------------

    function hideMenus() {
        folderMenu.classList.add("hidden");
        contentMenu.classList.add("hidden");
        documentMenu.classList.add("hidden");
    }


    function positionMenu(
        menu,
        clientX,
        clientY
    ) {
        const menuWidth = menu.offsetWidth;
        const menuHeight = menu.offsetHeight;

        const maxX =
            window.innerWidth
            - menuWidth
            - 8;

        const maxY =
            window.innerHeight
            - menuHeight
            - 8;

        menu.style.left =
            `${Math.max(
                8,
                Math.min(
                    clientX,
                    maxX
                )
            )}px`;

        menu.style.top =
            `${Math.max(
                8,
                Math.min(
                    clientY,
                    maxY
                )
            )}px`;
    }


    function showFolderMenu(
        event,
        element
    ) {
        event.preventDefault();

        hideMenus();

        selectedFolder = element;

        folderMenu.classList.remove(
            "hidden"
        );

        positionMenu(
            folderMenu,
            event.clientX,
            event.clientY
        );
    }


    function showContentMenu(
        event
    ) {
        event.preventDefault();

        hideMenus();

        selectedFolder = null;

        contentMenu.classList.remove(
            "hidden"
        );

        positionMenu(
            contentMenu,
            event.clientX,
            event.clientY
        );
    }

    function openDocument(row) {

        const openUrl =
            row.dataset.documentOpenUrl;

        if (!openUrl) {
            return;
        }

        window.open(
            openUrl,
            "_blank",
            "noopener"
        );
    }

    // -----------------------------------------------------------------
    // Clic droit sur dossier
    // -----------------------------------------------------------------

    document
        .querySelectorAll(
            "[data-folder-context]"
        )
        .forEach((element) => {

            element.addEventListener(
                "contextmenu",
                (event) => {
                    showFolderMenu(
                        event,
                        element
                    );
                }
            );

        });


    // -----------------------------------------------------------------
    // Clic droit sur la zone documentaire
    // -----------------------------------------------------------------

    documentContent.addEventListener(
        "contextmenu",
        (event) => {

            /*
             * Si le clic droit concerne déjà
             * un dossier, son menu spécifique
             * doit rester prioritaire.
             */
            if (
                event.target.closest(
                    "[data-folder-context]"
                )
            ) {
                return;
            }

            showContentMenu(
                event
            );
        }
    );

    contentImportDocument.addEventListener(
        "click",
        () => {

            hideMenus();

            const importUrl =
                documentContent.dataset
                    .folderImportUrl;

            if (!importUrl) {
                return;
            }

            window.location.href =
                importUrl.trim();
        }
    );

    documentRenameCancel.addEventListener(
        "click",
        () => {
            documentRenameDialog.close();
        }
    );

    documentMoveCancel.addEventListener(
        "click",
        () => {
            documentMoveDialog.close();
        }
    );

    documentCopyCancel.addEventListener(
        "click",
        () => {
            documentCopyDialog.close();
        }
    );

    // -----------------------------------------------------------------
    // Fermeture des menus
    // -----------------------------------------------------------------

    document.addEventListener(
        "click",
        (event) => {

            const clickInsideFolderMenu =
                folderMenu.contains(
                    event.target
                );

            const clickInsideContentMenu =
                contentMenu.contains(
                    event.target
                );

            if (
                !clickInsideFolderMenu
                && !clickInsideContentMenu
            ) {
                hideMenus();
            }
        }
    );


    window.addEventListener(
        "blur",
        hideMenus
    );


    window.addEventListener(
        "resize",
        hideMenus
    );


    // -----------------------------------------------------------------
    // Actions du menu dossier
    // -----------------------------------------------------------------

    folderMenu
        .querySelectorAll(
            "[data-folder-action]"
        )
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    if (!selectedFolder) {
                        return;
                    }

                    const action =
                        button.dataset.folderAction;

                    hideMenus();


                    // -------------------------------------------------
                    // Nouveau répertoire sous le dossier sélectionné
                    // -------------------------------------------------

                    if (action === "create") {

                        dialogTitle.textContent =
                            "Nouveau répertoire";

                        dialogForm.action =
                            selectedFolder.dataset
                                .folderCreateUrl;

                        parentInput.value =
                            selectedFolder.dataset
                                .folderId;

                        nameInput.value = "";

                        dialog.showModal();

                        nameInput.focus();

                        return;
                    }


                    // -------------------------------------------------
                    // Renommer
                    // -------------------------------------------------

                    if (action === "rename") {

                        dialogTitle.textContent =
                            "Renommer le répertoire";

                        dialogForm.action =
                            selectedFolder.dataset
                                .folderRenameUrl;

                        parentInput.value = "";

                        nameInput.value =
                            selectedFolder.dataset
                                .folderName;

                        dialog.showModal();

                        nameInput.select();

                        return;
                    }


                    // -------------------------------------------------
                    // Supprimer
                    // -------------------------------------------------

                    if (action === "delete") {

                        const folderName =
                            selectedFolder.dataset
                                .folderName;

                        const confirmed =
                            window.confirm(
                                `Supprimer le répertoire `
                                + `"${folderName}" ?`
                            );

                        if (!confirmed) {
                            return;
                        }

                        deleteForm.action =
                            selectedFolder.dataset
                                .folderDeleteUrl;

                        deleteForm.submit();
                    }
                }
            );

        });


    // -----------------------------------------------------------------
    // Nouveau répertoire depuis la zone documentaire
    // -----------------------------------------------------------------

    contentCreateFolder.addEventListener(
        "click",
        () => {

            hideMenus();

            dialogTitle.textContent =
                "Nouveau répertoire";

            dialogForm.action =
                documentContent.dataset
                    .folderCreateUrl;

            parentInput.value =
                documentContent.dataset
                    .currentFolderId || "";

            nameInput.value = "";

            dialog.showModal();

            nameInput.focus();
        }
    );


    // -----------------------------------------------------------------
    // Annulation boîte de dialogue
    // -----------------------------------------------------------------

    cancelButton.addEventListener(
        "click",
        () => {
            dialog.close();
        }
    );

});