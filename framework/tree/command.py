

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence

from framework.tree.node import TreeNodeKind


class TreeCommandTarget(StrEnum):
    """
    Zone d'application d'une commande.
    """

    WORKSPACE = "workspace"
    SELECTION = "selection"


@dataclass(frozen=True, slots=True)
class TreeCommandDefinition:
    """
    Décrit une commande disponible dans un environnement
    d'arborescence.

    Son URL, son activation effective et son exécution restent
    à la charge du module métier qui utilise l'arborescence.
    """

    identifier: str
    label: str
    icon: str
    target: TreeCommandTarget
    allowed_node_kinds: Sequence[TreeNodeKind] = ()
    order: int = 0

    def __post_init__(self) -> None:
        self._validate_identifier()
        self._validate_label()
        self._validate_icon()
        self._validate_target()
        self._validate_allowed_node_kinds()
        self._validate_order()

        object.__setattr__(
            self,
            "identifier",
            self.identifier.strip(),
        )
        object.__setattr__(
            self,
            "label",
            self.label.strip(),
        )
        object.__setattr__(
            self,
            "icon",
            self.icon.strip(),
        )
        object.__setattr__(
            self,
            "allowed_node_kinds",
            tuple(self.allowed_node_kinds),
        )

    def _validate_identifier(self) -> None:
        if not isinstance(self.identifier, str):
            raise TypeError(
                "L'identifiant d'une commande d'arborescence "
                "doit être une chaîne de caractères."
            )

        if not self.identifier.strip():
            raise ValueError(
                "L'identifiant d'une commande d'arborescence "
                "ne peut pas être vide."
            )

    def _validate_label(self) -> None:
        if not isinstance(self.label, str):
            raise TypeError(
                "Le libellé d'une commande d'arborescence "
                "doit être une chaîne de caractères."
            )

        if not self.label.strip():
            raise ValueError(
                "Le libellé d'une commande d'arborescence "
                "ne peut pas être vide."
            )

    def _validate_icon(self) -> None:
        if not isinstance(self.icon, str):
            raise TypeError(
                "L'icône d'une commande d'arborescence "
                "doit être une chaîne de caractères."
            )

        if not self.icon.strip():
            raise ValueError(
                "L'icône d'une commande d'arborescence "
                "ne peut pas être vide."
            )

    def _validate_target(self) -> None:
        if not isinstance(
            self.target,
            TreeCommandTarget,
        ):
            raise TypeError(
                "La cible d'une commande d'arborescence doit "
                "être une instance de TreeCommandTarget."
            )

    def _validate_allowed_node_kinds(self) -> None:
        if isinstance(
            self.allowed_node_kinds,
            (str, bytes),
        ):
            raise TypeError(
                "Les types de nœud autorisés doivent être "
                "une séquence de TreeNodeKind."
            )

        if not isinstance(
            self.allowed_node_kinds,
            Sequence,
        ):
            raise TypeError(
                "Les types de nœud autorisés doivent être "
                "une séquence de TreeNodeKind."
            )

        if (
            self.target == TreeCommandTarget.WORKSPACE
            and self.allowed_node_kinds
        ):
            raise ValueError(
                "Une commande d'espace de travail ne peut pas "
                "cibler un type de nœud."
            )

        seen_kinds = set()

        for node_kind in self.allowed_node_kinds:
            if not isinstance(node_kind, TreeNodeKind):
                raise TypeError(
                    "Chaque type de nœud autorisé doit être "
                    "une instance de TreeNodeKind."
                )

            if node_kind in seen_kinds:
                raise ValueError(
                    "Un type de nœud autorisé ne peut pas être "
                    "présent plusieurs fois."
                )

            seen_kinds.add(node_kind)

    def _validate_order(self) -> None:
        if (
            isinstance(self.order, bool)
            or not isinstance(self.order, int)
        ):
            raise TypeError(
                "L'ordre d'une commande d'arborescence "
                "doit être un entier."
            )