

document.addEventListener(
    "DOMContentLoaded",
    () => {
        const rootCreateFolderButton = (
            document.getElementById(
                "root-create-folder"
            )
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

        document
            .querySelectorAll("[data-tree]")
            .forEach((tree) => {
                const getSelectedBranch = () => {
                    return tree.querySelector(
                        'details[data-tree-selected="true"]'
                    );
                };

                const getTargetBranches = () => {
                    const selectedBranch = getSelectedBranch();

                    if (selectedBranch) {
                        return [
                            selectedBranch,
                            ...selectedBranch.querySelectorAll(
                                "details"
                            ),
                        ];
                    }

                    return [
                        ...tree.querySelectorAll("details"),
                    ];
                };

                const emptyArea = tree.querySelector(
                    "[data-tree-empty-area]"
                );

                emptyArea?.addEventListener(
                    "click",
                    () => {
                        const rootUrl = tree.dataset.treeRootUrl;

                        if (rootUrl) {
                            window.location.assign(rootUrl);
                        }
                    }
                );

                const updateActionLabels = () => {
                    const selectedBranch = getSelectedBranch();

                    tree
                        .querySelectorAll(
                            "[data-tree-action-label]"
                        )
                        .forEach((label) => {
                            label.textContent = selectedBranch
                                ? label.dataset.treeSelectedLabel
                                : label.dataset.treeGlobalLabel;
                        });
                };

                tree
                    .querySelectorAll(
                        '[data-tree-action="expand-all"]'
                    )
                    .forEach((button) => {
                        button.addEventListener(
                            "click",
                            () => {
                                getTargetBranches().forEach(
                                    (node) => {
                                        node.open = true;
                                    }
                                );
                            }
                        );
                    });

                tree
                    .querySelectorAll(
                        '[data-tree-action="collapse-all"]'
                    )
                    .forEach((button) => {
                        button.addEventListener(
                            "click",
                            () => {
                                getTargetBranches().forEach(
                                    (node) => {
                                        node.open = false;
                                    }
                                );
                            }
                        );
                    });

                updateActionLabels();
            });
    }
);