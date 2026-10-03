

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from framework.tree.command import TreeCommandDefinition


@dataclass(frozen=True, slots=True)
class TreeWorkspaceDefinition:
    """
    Décrit un environnement de travail d'une arborescence.

    Exemples : documentation, DOE, lot de signature.
    """

    identifier: str
    label: str
    icon: str
    commands: Sequence[TreeCommandDefinition] = ()

    def __post_init__(self) -> None:
        self._validate_identifier()
        self._validate_label()
        self._validate_icon()
        self._validate_commands()

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
            "commands",
            tuple(
                sorted(
                    self.commands,
                    key=lambda command: command.order,
                )
            ),
        )

    def _validate_identifier(self) -> None:
        if not isinstance(self.identifier, str):
            raise TypeError(
                "L'identifiant d'un environnement "
                "d'arborescence doit être une chaîne "
                "de caractères."
            )

        if not self.identifier.strip():
            raise ValueError(
                "L'identifiant d'un environnement "
                "d'arborescence ne peut pas être vide."
            )

    def _validate_label(self) -> None:
        if not isinstance(self.label, str):
            raise TypeError(
                "Le libellé d'un environnement d'arborescence "
                "doit être une chaîne de caractères."
            )

        if not self.label.strip():
            raise ValueError(
                "Le libellé d'un environnement d'arborescence "
                "ne peut pas être vide."
            )

    def _validate_icon(self) -> None:
        if not isinstance(self.icon, str):
            raise TypeError(
                "L'icône d'un environnement d'arborescence "
                "doit être une chaîne de caractères."
            )

        if not self.icon.strip():
            raise ValueError(
                "L'icône d'un environnement d'arborescence "
                "ne peut pas être vide."
            )

    def _validate_commands(self) -> None:
        if isinstance(self.commands, (str, bytes)):
            raise TypeError(
                "Les commandes d'un environnement "
                "d'arborescence doivent être une séquence."
            )

        if not isinstance(self.commands, Sequence):
            raise TypeError(
                "Les commandes d'un environnement "
                "d'arborescence doivent être une séquence."
            )

        identifiers = set()

        for command in self.commands:
            if not isinstance(
                command,
                TreeCommandDefinition,
            ):
                raise TypeError(
                    "Chaque commande d'environnement doit être "
                    "une instance de TreeCommandDefinition."
                )

            if command.identifier in identifiers:
                raise ValueError(
                    "Une commande ne peut pas être déclarée "
                    "plusieurs fois dans un environnement."
                )

            identifiers.add(command.identifier)