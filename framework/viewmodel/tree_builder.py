

from __future__ import annotations

from collections.abc import Mapping

from framework.runtime import EPTree, TreeCommand, TreeNode
from framework.tree import TreeNodeKind
from framework.viewmodel.tree import TreeViewModel
from framework.viewmodel.tree_command import (
    TreeCommandViewModel,
)
from framework.viewmodel.tree_node import TreeNodeViewModel
from framework.viewmodel.tree_workspace import (
    TreeWorkspaceViewModel,
)


class TreeViewModelBuilder:
    """
    Construit le ViewModel de présentation d'une arborescence.
    """

    __slots__ = ()

    def build(
        self,
        *,
        runtime: EPTree,
        expanded_node_identifiers: tuple[str, ...] = (),
        workspace_urls: Mapping[str, str] | None = None,
    ) -> TreeViewModel:
        """
        Construit un instantané de présentation.

        ``workspace_urls`` associe chaque environnement de travail
        à son URL de sélection.
        """

        self._validate_runtime(runtime)
        self._validate_expanded_node_identifiers(
            runtime=runtime,
            expanded_node_identifiers=expanded_node_identifiers,
        )
        self._validate_workspace_urls(
            runtime=runtime,
            workspace_urls=workspace_urls,
        )

        expanded_identifiers = set(
            expanded_node_identifiers,
        )

        if runtime.selected_node_identifier is not None:
            expanded_identifiers.update(
                self._get_selected_ancestor_identifiers(
                    runtime=runtime,
                )
            )

        children_by_parent = self._build_children_by_parent(
            runtime=runtime,
        )

        workspaces = self._build_workspaces(
            runtime=runtime,
            workspace_urls=workspace_urls,
        )

        active_workspace = next(
            workspace
            for workspace in workspaces
            if workspace.identifier
            == runtime.workspace.identifier
        )

        root_nodes = tuple(
            self._build_node(
                node=node,
                children_by_parent=children_by_parent,
                expanded_identifiers=expanded_identifiers,
                selected_node_identifier=(
                    runtime.selected_node_identifier
                ),
            )
            for node in runtime.root_nodes
        )

        return TreeViewModel(
            identifier=runtime.definition.identifier,
            workspaces=workspaces,
            active_workspace=active_workspace,
            root_nodes=root_nodes,
            commands=self._build_commands(
                runtime=runtime,
            ),
            selected_node_identifier=(
                runtime.selected_node_identifier
            ),
        )

    def _build_workspaces(
        self,
        *,
        runtime: EPTree,
        workspace_urls: Mapping[str, str] | None,
    ) -> tuple[TreeWorkspaceViewModel, ...]:
        return tuple(
            TreeWorkspaceViewModel(
                identifier=workspace.identifier,
                label=workspace.label,
                icon=workspace.icon,
                is_active=(
                    workspace.identifier
                    == runtime.workspace.identifier
                ),
                url=(
                    workspace_urls.get(workspace.identifier)
                    if workspace_urls is not None
                    else None
                ),
            )
            for workspace in runtime.definition.workspaces
        )

    def _build_commands(
        self,
        *,
        runtime: EPTree,
    ) -> tuple[TreeCommandViewModel, ...]:
        return tuple(
            self._build_command(command)
            for command in runtime.commands
            if command.is_visible
        )

    @staticmethod
    def _build_command(
        command: TreeCommand,
    ) -> TreeCommandViewModel:
        return TreeCommandViewModel(
            identifier=command.definition.identifier,
            label=command.definition.label,
            icon=command.definition.icon,
            target=command.definition.target,
            url=command.url,
            method=command.method,
            is_enabled=command.is_enabled,
        )

    def _build_children_by_parent(
        self,
        *,
        runtime: EPTree,
    ) -> dict[str, tuple[TreeNode, ...]]:
        children_by_parent: dict[str, list[TreeNode]] = {}

        for node in runtime.nodes:
            if node.parent_identifier is None:
                continue

            children_by_parent.setdefault(
                node.parent_identifier,
                [],
            ).append(node)

        return {
            parent_identifier: tuple(children)
            for parent_identifier, children in (
                children_by_parent.items()
            )
        }

    def _build_node(
        self,
        *,
        node: TreeNode,
        children_by_parent: dict[str, tuple[TreeNode, ...]],
        expanded_identifiers: set[str],
        selected_node_identifier: str | None,
    ) -> TreeNodeViewModel:
        children = tuple(
            self._build_node(
                node=child,
                children_by_parent=children_by_parent,
                expanded_identifiers=expanded_identifiers,
                selected_node_identifier=(
                    selected_node_identifier
                ),
            )
            for child in children_by_parent.get(
                node.identifier,
                (),
            )
        )

        return TreeNodeViewModel(
            identifier=node.identifier,
            label=node.label,
            kind=node.kind,
            icon=self._get_node_icon(
                node,
            ),
            url=node.url,
            is_selected=(
                node.identifier
                == selected_node_identifier
            ),
            is_expanded=(
                node.identifier
                in expanded_identifiers
            ),
            is_disabled=node.is_disabled,
            data_attributes=node.data_attributes,
            children=children,
            source_object=node.source_object,
        )

    @staticmethod
    def _get_node_icon(
        node: TreeNode,
    ) -> str:
        """
        Retourne l'icône explicite du nœud ou son icône par défaut.
        """

        if node.icon is not None:
            return node.icon

        if node.kind is TreeNodeKind.BRANCH:
            return "folder"

        return "file"

    @staticmethod
    def _get_selected_ancestor_identifiers(
        *,
        runtime: EPTree,
    ) -> set[str]:
        if runtime.selected_node_identifier is None:
            return set()

        nodes_by_identifier = {
            node.identifier: node
            for node in runtime.nodes
        }

        ancestors: set[str] = set()
        current_node = nodes_by_identifier[
            runtime.selected_node_identifier
        ]

        while current_node.parent_identifier is not None:
            parent_identifier = current_node.parent_identifier
            ancestors.add(parent_identifier)
            current_node = nodes_by_identifier[
                parent_identifier
            ]

        return ancestors

    @staticmethod
    def _validate_runtime(runtime: object) -> None:
        if not isinstance(runtime, EPTree):
            raise TypeError(
                "La propriété 'runtime' doit être une instance "
                "de EPTree."
            )

    @staticmethod
    def _validate_expanded_node_identifiers(
        *,
        runtime: EPTree,
        expanded_node_identifiers: object,
    ) -> None:
        if not isinstance(
            expanded_node_identifiers,
            tuple,
        ):
            raise TypeError(
                "Les identifiants des nœuds ouverts doivent être "
                "fournis sous la forme d'un tuple."
            )

        nodes_by_identifier = {
            node.identifier: node
            for node in runtime.nodes
        }

        for identifier in expanded_node_identifiers:
            if not isinstance(identifier, str):
                raise TypeError(
                    "Chaque identifiant de nœud ouvert doit être "
                    "une chaîne de caractères."
                )

            if not identifier.strip():
                raise ValueError(
                    "Un identifiant de nœud ouvert ne peut pas "
                    "être vide."
                )

            try:
                node = nodes_by_identifier[identifier]
            except KeyError as exc:
                raise ValueError(
                    f"Le nœud ouvert {identifier!r} n'existe pas "
                    "dans cette arborescence."
                ) from exc

            if node.kind is not TreeNodeKind.BRANCH:
                raise ValueError(
                    "Seuls les nœuds de type BRANCH peuvent être "
                    "marqués comme ouverts."
                )

    @staticmethod
    def _validate_workspace_urls(
        *,
        runtime: EPTree,
        workspace_urls: object,
    ) -> None:
        if workspace_urls is None:
            return

        if not isinstance(workspace_urls, Mapping):
            raise TypeError(
                "La propriété 'workspace_urls' doit être "
                "un Mapping."
            )

        workspace_identifiers = {
            workspace.identifier
            for workspace in runtime.definition.workspaces
        }

        for identifier, url in workspace_urls.items():
            if not isinstance(identifier, str):
                raise TypeError(
                    "Chaque identifiant d'environnement doit être "
                    "une chaîne de caractères."
                )

            if identifier not in workspace_identifiers:
                raise ValueError(
                    f"L'environnement {identifier!r} n'existe pas "
                    "dans cette arborescence."
                )

            if not isinstance(url, str):
                raise TypeError(
                    "Chaque URL d'environnement doit être une "
                    "chaîne de caractères."
                )

            if not url.strip():
                raise ValueError(
                    "Une URL d'environnement ne peut pas être vide."
                )