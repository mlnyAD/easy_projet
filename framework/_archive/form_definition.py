

from __future__ import annotations

from framework.dictionary.entity import EntityDefinition
from framework.dictionary.field import FieldDefinition


class FormDefinition:
    """Décrit un formulaire métier."""

    def __init__(
        self,
        entity: EntityDefinition,
        fields: list[FieldDefinition],
    ) -> None:
        self._entity = entity
        self._fields = fields

    @classmethod
    def from_entity(
        cls,
        entity: EntityDefinition,
    ) -> "FormDefinition":
        return cls(
            entity=entity,
            fields=list(entity.fields.values()),
        )

    @property
    def entity(self) -> EntityDefinition:
        return self._entity

    @property
    def fields(self) -> list[FieldDefinition]:
        return self._fields