

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from .field import FieldDefinition
from .validator import DictionaryValidator


class EntityDefinition:
    """
    Représentation en lecture seule d'une entité métier.

    La validation est assurée par DictionaryValidator.
    Cette classe fournit une API objet stable au Framework.
    """

    def __init__(self, definition: Mapping[str, Any]) -> None:
        self._definition = definition

        self._fields = MappingProxyType(
            {
                field_name: FieldDefinition(
                    name=field_name,
                    definition=field_definition,
                )
                for field_name, field_definition in definition["fields"].items()
            }
        )

    @property
    def name(self) -> str:
        return self._definition["entity"]["name"]

    @property
    def label(self) -> str:
        return self._definition["entity"]["label"]

    @property
    def label_plural(self) -> str:
        return self._definition["entity"]["label_plural"]

    @property
    def description(self) -> str:
        return self._definition["entity"].get("description", "")

    @property
    def fields(self) -> Mapping[str, FieldDefinition]:
        """
        Ensemble des champs de l'entité.

        Les valeurs sont des FieldDefinition.
        """
        return self._fields

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(self._fields.keys())

    @property
    def identifier_name(self) -> str | None:
        for field in self._fields.values():
            if field.identifier:
                return field.name

        return None

    @property
    def identifier(self) -> FieldDefinition | None:
        identifier_name = self.identifier_name

        if identifier_name is None:
            return None

        return self._fields[identifier_name]

    def has_field(self, field_name: str) -> bool:
        return field_name in self._fields

    def get_field(self, field_name: str) -> FieldDefinition:
        try:
            return self._fields[field_name]
        except KeyError as exc:
            raise KeyError(
                f"Le champ '{field_name}' n'existe pas "
                f"dans l'entité '{self.name}'."
            ) from exc

    def __iter__(self):
        return iter(self._fields.values())

    def __len__(self) -> int:
        return len(self._fields)

    def __contains__(self, field_name: str) -> bool:
        return field_name in self._fields

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"fields={len(self)}"
            f")"
        )
       
    @classmethod
    def from_dictionary(
        cls,
        definition: Mapping[str, Any],
    ) -> "EntityDefinition":
        """
        Construit une EntityDefinition à partir d'un
        dictionnaire métier validé.
        """
        DictionaryValidator().validate(definition)
        return cls(definition) 