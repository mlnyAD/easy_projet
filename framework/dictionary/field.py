

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any


@dataclass(frozen=True, slots=True, init=False)
class FieldDefinition:
    """
    Représentation en lecture seule d'un champ décrit
    par un dictionnaire métier Easy Projet.

    La validation du contenu reste sous la responsabilité
    de DictionaryValidator.
    """

    name: str
    _definition: Mapping[str, Any]

    def __init__(
        self,
        name: str,
        definition: Mapping[str, Any],
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(
            self,
            "_definition",
            MappingProxyType(dict(definition)),
        )

    @property
    def label(self) -> str:
        """Retourne le libellé utilisateur du champ."""
        return self._definition["label"]

    @property
    def data_type(self) -> str:
        """Retourne le type métier du champ."""
        return self._definition["data_type"]

    @property
    def description(self) -> str:
        """Retourne la description du champ."""
        return self._definition.get("description", "")

    @property
    def required(self) -> bool:
        """Indique si le champ est obligatoire."""
        return self._definition.get("required", False)

    @property
    def identifier(self) -> bool:
        """Indique si le champ est l'identifiant de l'entité."""
        return self._definition.get("identifier", False)

    @property
    def unique(self) -> bool:
        """Indique si la valeur du champ doit être unique."""
        return self._definition.get("unique", False)

    @property
    def max_length(self) -> int | None:
        """Retourne la longueur maximale autorisée."""
        return self._definition.get("max_length")

    @property
    def default(self) -> Any:
        """Retourne la valeur par défaut du champ."""
        return self._definition.get("default")

    @property
    def definition(self) -> Mapping[str, Any]:
        """Retourne la définition complète en lecture seule."""
        return self._definition

    def get(self, property_name: str, default: Any = None) -> Any:
        """Retourne une propriété facultative du champ."""
        return self._definition.get(property_name, default)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"data_type={self.data_type!r}"
            f")"
        )