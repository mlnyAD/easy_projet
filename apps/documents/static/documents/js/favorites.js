

"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const content = document.getElementById(
        "favorite-document-content"
    );
    const menu = document.getElementById(
        "favorite-document-context-menu"
    );

    if (!content || !menu) {
        return;
    }

    const rows = document.querySelectorAll(
        "[data-favorite-document-row]"
    );

    const renameDialog = document.getElementById(
        "document-rename-dialog"
    );
    const renameForm = document.getElementById(
        "document-rename-form"
    );
    const renameTitle = document.getElementById(
        "document-rename-title"
    );
    const renameCancel = document.getElementById(
        "document-rename-cancel"
    );

    const moveDialog = document.getElementById(
        "document-move-dialog"
    );
    const moveForm = document.getElementById(
        "document-move-form"
    );
    const moveDestination = document.getElementById(
        "document-move-destination"
    );
    const moveCancel = document.getElementById(
        "document-move-cancel"
    );

    const copyDialog = document.getElementById(
        "document-copy-dialog"
    );
    const copyForm = document.getElementById(
        "document-copy-form"
    );
    const copyTitle = document.getElementById(
        "document-copy-title"
    );
    const copyDestination = document.getElementById(
        "document-copy-destination"
    );
    const copyCancel = document.getElementById(
        "document-copy-cancel"
    );

    let selectedRow = null;

    function hideMenu() {
        menu.classList.add("hidden");
    }

    function positionMenu(clientX, clientY) {
        const maxX = window.innerWidth - menu.offsetWidth - 8;
        const maxY = window.innerHeight - menu.offsetHeight - 8;

        menu.style.left = `${Math.max(
            8,
            Math.min(clientX, maxX)
        )}px`;

        menu.style.top = `${Math.max(
            8,
            Math.min(clientY, maxY)
        )}px`;
    }

    function selectRow(row) {
        if (selectedRow) {
            selectedRow.classList.remove(
                "bg-axcio-surface-alt",
                "dark:bg-axcio-surface-alt-dark"
            );
        }

        selectedRow = row;

        selectedRow.classList.add(
            "bg-axcio-surface-alt",
            "dark:bg-axcio-surface-alt-dark"
        );
    }

    function openDocument(row) {
        const url = row.dataset.documentOpenUrl;

        if (url) {
            window.open(url, "_blank", "noopener");
        }
    }

    function submitPost(url) {
        if (!url) {
            return;
        }

        const csrfToken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );

        if (!csrfToken) {
            return;
        }

        const form = document.createElement("form");
        const csrfInput = document.createElement("input");

        form.method = "post";
        form.action = url;

        csrfInput.type = "hidden";
        csrfInput.name = "csrfmiddlewaretoken";
        csrfInput.value = csrfToken.value;

        const nextInput = document.createElement("input");

        nextInput.type = "hidden";
        nextInput.name = "next";
        nextInput.value = (
            window.location.pathname
            + window.location.search
        );

        form.appendChild(csrfInput);
        form.appendChild(nextInput);
        document.body.appendChild(form);

        form.submit();
    }

    function setDestinationOptions(select, row) {
        const template = document.querySelector(
            "[data-document-destination-options="
            + `"${row.dataset.documentId}"]`
        );

        if (!template) {
            return false;
        }

        select.innerHTML = template.innerHTML;
        select.value = row.dataset.documentFolderId || "";

        return true;
    }

    function updateMenuForRow(row) {
        const canWork = (
            row.dataset.documentCanWork === "true"
        );

        menu.querySelectorAll(
            "[data-document-work-action], "
            + "[data-document-work-separator]"
        ).forEach((element) => {
            element.classList.toggle("hidden", !canWork);
        });
    }

    rows.forEach((row) => {
        row.addEventListener("click", () => {
            selectRow(row);
        });

        row.addEventListener("dblclick", () => {
            openDocument(row);
        });

        row.addEventListener("contextmenu", (event) => {
            event.preventDefault();

            selectRow(row);
            updateMenuForRow(row);

            menu.classList.remove("hidden");
            positionMenu(event.clientX, event.clientY);

            window.lucide?.createIcons();
        });
    });

    menu.querySelectorAll(
        "[data-document-action]"
    ).forEach((button) => {
        button.addEventListener("click", () => {
            if (!selectedRow) {
                return;
            }

            const action = button.dataset.documentAction;
            const canWork = (
                selectedRow.dataset.documentCanWork === "true"
            );

            hideMenu();

            if (action === "open") {
                openDocument(selectedRow);
                return;
            }

            if (action === "download") {
                const url = (
                    selectedRow.dataset.documentDownloadUrl
                );

                if (url) {
                    window.location.assign(url);
                }

                return;
            }

            if (action === "properties") {
                window.location.assign(
                    selectedRow.dataset
                        .documentPropertiesUrl
                );
                return;
            }

            if (!canWork) {
                return;
            }

            if (action === "rename") {
                if (!renameForm || !renameDialog) {
                    return;
                }

                renameForm.action = (
                    selectedRow.dataset.documentRenameUrl
                );
                renameTitle.value = (
                    selectedRow.dataset.documentTitle
                );

                renameDialog.showModal();
                renameTitle.focus();
                renameTitle.select();

                return;
            }

            if (action === "move") {
                if (
                    !moveForm
                    || !moveDialog
                    || !setDestinationOptions(
                        moveDestination,
                        selectedRow
                    )
                ) {
                    return;
                }

                moveForm.action = (
                    selectedRow.dataset.documentMoveUrl
                );

                moveDialog.showModal();
                moveDestination.focus();

                return;
            }

            if (action === "copy") {
                if (
                    !copyForm
                    || !copyDialog
                    || !setDestinationOptions(
                        copyDestination,
                        selectedRow
                    )
                ) {
                    return;
                }

                copyForm.action = (
                    selectedRow.dataset.documentCopyUrl
                );
                copyTitle.value = (
                    selectedRow.dataset.documentTitle
                );

                copyDialog.showModal();
                copyTitle.focus();
                copyTitle.select();

                return;
            }

            if (action === "sign") {
                window.location.assign(
                    selectedRow.dataset
                        .documentSignatureUrl
                );
                return;
            }

            if (action === "favorite") {
                submitPost(
                    selectedRow.dataset
                        .documentFavoriteRemoveUrl
                );
                return;
            }

            if (action === "delete") {
                const title = (
                    selectedRow.dataset.documentTitle
                );

                if (
                    window.confirm(
                        `Mettre le document "${title}" `
                        + "à la corbeille ?\n\n"
                        + "Il pourra être restauré depuis "
                        + "la corbeille."
                    )
                ) {
                    submitPost(
                        selectedRow.dataset
                            .documentDeleteUrl
                    );
                }
            }
        });
    });

    renameCancel?.addEventListener("click", () => {
        renameDialog?.close();
    });

    moveCancel?.addEventListener("click", () => {
        moveDialog?.close();
    });

    copyCancel?.addEventListener("click", () => {
        copyDialog?.close();
    });

    document.addEventListener("click", (event) => {
        if (!menu.contains(event.target)) {
            hideMenu();
        }
    });

    window.addEventListener("blur", hideMenu);
    window.addEventListener("resize", hideMenu);
});