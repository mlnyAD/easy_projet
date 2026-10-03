

from __future__ import annotations

from collections.abc import Iterator, Sequence
from types import MappingProxyType

from framework.tree.workspace import TreeWorkspaceDefinition


class TreeDefinition:
    """
    Décrit une arborescence réutilisable du framework.

    La définition ne dépend ni de Django, ni des modèles métier,
    ni du mécanisme de rendu.
    """

    __slots__ = (
        "_identifier",
        "_workspaces",
        "_workspaces_by_identifier",
    )

    def __init__(
        self,
        *,
        identifier: str,
        workspaces: Sequence[TreeWorkspaceDefinition],
    ) -> None:
        self._validate_identifier(identifier)
        self._validate_workspaces(workspaces)

        normalized_workspaces = tuple(workspaces)

        self._identifier = identifier.strip()
        self._workspaces = normalized_workspaces
        self._workspaces_by_identifier = MappingProxyType(
            {
                workspace.identifier: workspace
                for workspace in normalized_workspaces
            }
        )

    @property
    def identifier(self) -> str:
        """Retourne l'identifiant stable de l'arborescence."""
        return self._identifier

    @property
    def workspaces(
        self,
    ) -> tuple[TreeWorkspaceDefinition, ...]:
        """Retourne les environnements disponibles."""
        return self._workspaces

    @property
    def workspaces_by_identifier(
        self,
    ) -> MappingProxyType[str, TreeWorkspaceDefinition]:
        """Retourne l'index immuable des environnements."""
        return self._workspaces_by_identifier

    def has_workspace(
        self,
        identifier: str,
    ) -> bool:
        """Indique si l'environnement existe."""
        return identifier in self._workspaces_by_identifier

    def get_workspace(
        self,
        identifier: str,
    ) -> TreeWorkspaceDefinition:
        """
        Retourne l'environnement demandé.

        Lève KeyError lorsqu'il n'existe pas.
        """
        return self._workspaces_by_identifier[identifier]

    def __iter__(self) -> Iterator[TreeWorkspaceDefinition]:
        return iter(self._workspaces)

    def __len__(self) -> int:
        return len(self._workspaces)

    def __contains__(self, identifier: object) -> bool:
        return identifier in self._workspaces_by_identifier

    @staticmethod
    def _validate_identifier(identifier: object) -> None:
        if not isinstance(identifier, str):
            raise TypeError(
                "L'identifiant d'une arborescence doit être "
                "une chaîne de caractères."
            )

        if not identifier.strip():
            raise ValueError(
                "L'identifiant d'une arborescence ne peut pas "
                "être vide."
            )

    @staticmethod
    def _validate_workspaces(workspaces: object) -> None:
        if isinstance(workspaces, (str, bytes)):
            raise TypeError(
                "Les environnements d'une arborescence doivent "
                "être une séquence."
            )

        if not isinstance(workspaces, Sequence):
            raise TypeError(
                "Les environnements d'une arborescence doivent "
                "être une séquence."
            )

        if not workspaces:
            raise ValueError(
                "Une arborescence doit définir au moins "
                "un environnement."
            )

        identifiers = set()

        for workspace in workspaces:
            if not isinstance(
                workspace,
                TreeWorkspaceDefinition,
            ):
                raise TypeError(
                    "Chaque environnement doit être une instance "
                    "de TreeWorkspaceDefinition."
                )

            if workspace.identifier in identifiers:
                raise ValueError(
                    "Un environnement ne peut pas être déclaré "
                    "plusieurs fois."
                )

            identifiers.add(workspace.identifier)