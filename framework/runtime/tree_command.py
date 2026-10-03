

from __future__ import annotations

from dataclasses import dataclass

from framework.tree import TreeCommandDefinition


@dataclass(frozen=True, slots=True)
class TreeCommand:
    """
    État dynamique d'une commande d'arborescence.

    La définition décrit la commande. Cette classe porte son URL,
    sa méthode HTTP et son état effectif dans l'environnement actif.
    """

    definition: TreeCommandDefinition
    url: str | None = None
    method: str = "GET"
    is_visible: bool = True
    is_enabled: bool = True

    def __post_init__(self) -> None:
        self._validate_definition()
        self._validate_url()
        self._validate_method()
        self._validate_is_visible()
        self._validate_is_enabled()

        object.__setattr__(
            self,
            "url",
            (
                self.url.strip()
                if self.url is not None
                else None
            ),
        )
        object.__setattr__(
            self,
            "method",
            self.method.upper(),
        )

    def _validate_definition(self) -> None:
        if not isinstance(
            self.definition,
            TreeCommandDefinition,
        ):
            raise TypeError(
                "La définition d'une commande doit être une "
                "instance de TreeCommandDefinition."
            )

    def _validate_url(self) -> None:
        if self.url is None:
            return

        if not isinstance(self.url, str):
            raise TypeError(
                "L'URL d'une commande doit être une chaîne "
                "de caractères ou None."
            )

        if not self.url.strip():
            raise ValueError(
                "L'URL d'une commande ne peut pas être vide."
            )

    def _validate_method(self) -> None:
        if not isinstance(self.method, str):
            raise TypeError(
                "La méthode HTTP d'une commande doit être "
                "une chaîne de caractères."
            )

        if self.method.upper() not in {"GET", "POST"}:
            raise ValueError(
                "La méthode HTTP d'une commande doit être "
                "GET ou POST."
            )

    def _validate_is_visible(self) -> None:
        if not isinstance(self.is_visible, bool):
            raise TypeError(
                "L'état visible d'une commande doit être "
                "un booléen."
            )

    def _validate_is_enabled(self) -> None:
        if not isinstance(self.is_enabled, bool):
            raise TypeError(
                "L'état activé d'une commande doit être "
                "un booléen."
            )