

from __future__ import annotations

from collections.abc import Iterator, Sequence
from types import MappingProxyType

from framework.runtime.tree_command import TreeCommand
from framework.runtime.tree_node import TreeNode
from framework.tree import (
    TreeCommandTarget,
    TreeDefinition,
    TreeNodeKind,
)


class EPTree:
    """
    Exécution d'une arborescence dans un environnement donné.

    Cette classe ne connaît ni Django, ni la base de données,
    ni le rendu HTML.
    """

    __slots__ = (
        "_definition",
        "_workspace_identifier",
        "_nodes",
        "_nodes_by_identifier",
        "_children_by_parent_identifier",
        "_commands",
        "_selected_node_identifier",
    )

    def __init__(
        self,
        *,
        definition: TreeDefinition,
        workspace_identifier: str,
        nodes: Sequence[TreeNode],
        commands: Sequence[TreeCommand] = (),
        selected_node_identifier: str | None = None,
    ) -> None:
        self._validate_definition(definition)
        self._validate_workspace_identifier(
            definition=definition,
            workspace_identifier=workspace_identifier,
        )
        self._validate_nodes(nodes)
        self._validate_commands(
            definition=definition,
            workspace_identifier=workspace_identifier,
            commands=commands,
        )
        self._validate_selected_node_identifier(
            nodes=nodes,
            selected_node_identifier=selected_node_identifier,
        )
        self._validate_node_hierarchy(nodes)

        normalized_nodes = tuple(nodes)
        normalized_commands = tuple(commands)

        self._definition = definition
        self._workspace_identifier = (
            workspace_identifier.strip()
        )
        self._nodes = normalized_nodes
        self._nodes_by_identifier = MappingProxyType(
            {
                node.identifier: node
                for node in normalized_nodes
            }
        )
        self._children_by_parent_identifier = (
            self._build_children_by_parent_identifier(
                nodes=normalized_nodes,
            )
        )
        self._commands = normalized_commands
        self._selected_node_identifier = (
            selected_node_identifier.strip()
            if selected_node_identifier is not None
            else None
        )

    @property
    def definition(self) -> TreeDefinition:
        """Retourne la définition structurelle."""
        return self._definition

    @property
    def workspace_identifier(self) -> str:
        """Retourne l'identifiant de l'environnement actif."""
        return self._workspace_identifier

    @property
    def workspace(self):
        """Retourne la définition de l'environnement actif."""
        return self._definition.get_workspace(
            self._workspace_identifier
        )

    @property
    def nodes(self) -> tuple[TreeNode, ...]:
        """Retourne les nœuds dans leur ordre de déclaration."""
        return self._nodes

    @property
    def commands(self) -> tuple[TreeCommand, ...]:
        """Retourne les commandes résolues de l'environnement."""
        return self._commands

    @property
    def selected_node_identifier(self) -> str | None:
        """Retourne l'identifiant du nœud sélectionné."""
        return self._selected_node_identifier

    @property
    def selected_node(self) -> TreeNode | None:
        """Retourne le nœud sélectionné, lorsqu'il existe."""
        if self._selected_node_identifier is None:
            return None

        return self._nodes_by_identifier[
            self._selected_node_identifier
        ]

    @property
    def root_nodes(self) -> tuple[TreeNode, ...]:
        """Retourne les nœuds racines."""
        return self.get_children()

    def get_node(
        self,
        identifier: str,
    ) -> TreeNode:
        """
        Retourne le nœud demandé.

        Lève KeyError lorsque le nœud n'existe pas.
        """
        return self._nodes_by_identifier[identifier]

    def has_node(
        self,
        identifier: str,
    ) -> bool:
        """Indique si un nœud existe."""
        return identifier in self._nodes_by_identifier

    def get_children(
        self,
        parent_identifier: str | None = None,
    ) -> tuple[TreeNode, ...]:
        """Retourne les enfants d'un nœud ou les racines."""
        return self._children_by_parent_identifier.get(
            parent_identifier,
            (),
        )

    def __iter__(self) -> Iterator[TreeNode]:
        return iter(self._nodes)

    def __len__(self) -> int:
        return len(self._nodes)

    def _validate_definition(
        self,
        definition: object,
    ) -> None:
        if not isinstance(definition, TreeDefinition):
            raise TypeError(
                "La propriété 'definition' doit être une "
                "instance de TreeDefinition."
            )

    def _validate_workspace_identifier(
        self,
        *,
        definition: TreeDefinition,
        workspace_identifier: object,
    ) -> None:
        if not isinstance(workspace_identifier, str):
            raise TypeError(
                "L'identifiant de l'environnement actif doit "
                "être une chaîne de caractères."
            )

        normalized_identifier = workspace_identifier.strip()

        if not normalized_identifier:
            raise ValueError(
                "L'identifiant de l'environnement actif ne peut "
                "pas être vide."
            )

        if not definition.has_workspace(
            normalized_identifier
        ):
            raise ValueError(
                "L'environnement actif n'existe pas dans "
                "la définition de l'arborescence."
            )

    def _validate_nodes(
        self,
        nodes: object,
    ) -> None:
        if isinstance(nodes, (str, bytes)):
            raise TypeError(
                "Les nœuds d'une arborescence doivent être "
                "une séquence de TreeNode."
            )

        if not isinstance(nodes, Sequence):
            raise TypeError(
                "Les nœuds d'une arborescence doivent être "
                "une séquence de TreeNode."
            )

        identifiers = set()

        for node in nodes:
            if not isinstance(node, TreeNode):
                raise TypeError(
                    "Chaque nœud doit être une instance "
                    "de TreeNode."
                )

            if node.identifier in identifiers:
                raise ValueError(
                    "Un identifiant de nœud ne peut pas être "
                    "présent plusieurs fois."
                )

            identifiers.add(node.identifier)

    def _validate_commands(
        self,
        *,
        definition: TreeDefinition,
        workspace_identifier: str,
        commands: object,
    ) -> None:
        if isinstance(commands, (str, bytes)):
            raise TypeError(
                "Les commandes d'une arborescence doivent être "
                "une séquence de TreeCommand."
            )

        if not isinstance(commands, Sequence):
            raise TypeError(
                "Les commandes d'une arborescence doivent être "
                "une séquence de TreeCommand."
            )

        workspace = definition.get_workspace(
            workspace_identifier.strip()
        )
        available_command_identifiers = {
            command.identifier
            for command in workspace.commands
        }
        command_identifiers = set()

        for command in commands:
            if not isinstance(command, TreeCommand):
                raise TypeError(
                    "Chaque commande doit être une instance "
                    "de TreeCommand."
                )

            identifier = command.definition.identifier

            if identifier not in available_command_identifiers:
                raise ValueError(
                    f"La commande {identifier!r} n'est pas "
                    "déclarée dans l'environnement actif."
                )

            if identifier in command_identifiers:
                raise ValueError(
                    "Une commande ne peut pas être résolue "
                    "plusieurs fois."
                )

            command_identifiers.add(identifier)

    def _validate_selected_node_identifier(
        self,
        *,
        nodes: Sequence[TreeNode],
        selected_node_identifier: object,
    ) -> None:
        if selected_node_identifier is None:
            return

        if not isinstance(selected_node_identifier, str):
            raise TypeError(
                "L'identifiant du nœud sélectionné doit être "
                "une chaîne de caractères ou None."
            )

        normalized_identifier = selected_node_identifier.strip()

        if not normalized_identifier:
            raise ValueError(
                "L'identifiant du nœud sélectionné ne peut pas "
                "être vide."
            )

        if normalized_identifier not in {
            node.identifier
            for node in nodes
        }:
            raise ValueError(
                "Le nœud sélectionné n'existe pas dans "
                "l'arborescence."
            )

    def _validate_node_hierarchy(
        self,
        nodes: Sequence[TreeNode],
    ) -> None:
        nodes_by_identifier = {
            node.identifier: node
            for node in nodes
        }

        for node in nodes:
            parent_identifier = node.parent_identifier

            if parent_identifier is None:
                continue

            parent = nodes_by_identifier.get(
                parent_identifier
            )

            if parent is None:
                raise ValueError(
                    f"Le parent du nœud {node.identifier!r} "
                    "n'existe pas dans l'arborescence."
                )

            if parent.kind != TreeNodeKind.BRANCH:
                raise ValueError(
                    f"Le parent du nœud {node.identifier!r} "
                    "doit être de type BRANCH."
                )

            self._validate_no_cycle(
                node=node,
                nodes_by_identifier=nodes_by_identifier,
            )

    @staticmethod
    def _validate_no_cycle(
        *,
        node: TreeNode,
        nodes_by_identifier: dict[str, TreeNode],
    ) -> None:
        visited_identifiers = {
            node.identifier,
        }
        parent_identifier = node.parent_identifier

        while parent_identifier is not None:
            if parent_identifier in visited_identifiers:
                raise ValueError(
                    "La hiérarchie d'arborescence contient "
                    "une boucle."
                )

            visited_identifiers.add(parent_identifier)

            parent = nodes_by_identifier[
                parent_identifier
            ]
            parent_identifier = parent.parent_identifier

    @staticmethod
    def _build_children_by_parent_identifier(
        *,
        nodes: tuple[TreeNode, ...],
    ) -> MappingProxyType[
        str | None,
        tuple[TreeNode, ...],
    ]:
        children_by_parent_identifier: dict[
            str | None,
            list[TreeNode],
        ] = {}

        for node in nodes:
            children_by_parent_identifier.setdefault(
                node.parent_identifier,
                [],
            ).append(node)

        return MappingProxyType(
            {
                parent_identifier: tuple(children)
                for (
                    parent_identifier,
                    children,
                ) in children_by_parent_identifier.items()
            }
        )