

document.addEventListener(
    "DOMContentLoaded",
    () => {
        const rootCreateFolderButton =
            document.getElementById(
                "root-create-folder"
            );

        document
            .querySelectorAll(
                '[data-tree-command="create-root-folder"]'
            )
            .forEach((button) => {
                button.addEventListener(
                    "click",
                    () => {
                        if (!rootCreateFolderButton) {
                            return;
                        }

                        rootCreateFolderButton.click();
                    }
                );
            });
    }
);