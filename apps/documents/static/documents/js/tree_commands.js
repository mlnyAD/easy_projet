

document.addEventListener(
    "DOMContentLoaded",
    () => {
        const treeStateStoragePrefix = (
            "easy-projet-tree-open:"
        );

        const getTreeStateKey = (tree) => {
            const rootUrl = (
                tree.dataset.treeRootUrl
                || window.location.pathname
            );

            return (
                treeStateStoragePrefix
                + rootUrl
            );
        };

        const getStoredOpenNodeIds = (tree) => {
            try {
                const value = window.sessionStorage.getItem(
                    getTreeStateKey(tree)
                );

                if (!value) {
                    return null;
                }

                const nodeIds = JSON.parse(value);

                if (!Array.isArray(nodeIds)) {
                    return null;
                }

                return new Set(
                    nodeIds.filter(
                        (nodeId) => (
                            typeof nodeId === "string"
                        )
                    )
                );
            } catch (_error) {
                return null;
            }
        };

        const storeOpenNodeIds = (tree) => {
            const nodeIds = [
                ...tree.querySelectorAll(
                    "details[data-tree-node-id][open]"
                ),
            ]
                .map(
                    (node) => (
                        node.dataset.treeNodeId
                    )
                )
                .filter(Boolean);

            try {
                window.sessionStorage.setItem(
                    getTreeStateKey(tree),
                    JSON.stringify(nodeIds)
                );
            } catch (_error) {
                // Le fonctionnement de l'arborescence ne dépend pas
                // du stockage navigateur.
            }
        };

        const restoreOpenNodeIds = (tree) => {
            const openNodeIds = getStoredOpenNodeIds(tree);

            if (openNodeIds === null) {
                return;
            }

            tree
                .querySelectorAll(
                    "details[data-tree-node-id]"
                )
                .forEach((node) => {
                    node.open = openNodeIds.has(
                        node.dataset.treeNodeId
                    );
                });
        };

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

                restoreOpenNodeIds(tree);

                tree
                    .querySelectorAll(
                        "details[data-tree-node-id]"
                    )
                    .forEach((node) => {
                        node.addEventListener(
                            "toggle",
                            () => {
                                storeOpenNodeIds(tree);
                            }
                        );
                    });

                window.addEventListener(
                    "pagehide",
                    () => {
                        storeOpenNodeIds(tree);
                    }
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

                                storeOpenNodeIds(tree);
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

                                storeOpenNodeIds(tree);
                            }
                        );
                    });

                updateActionLabels();
            });
    }
);