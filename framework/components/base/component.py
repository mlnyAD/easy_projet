

from __future__ import annotations

from framework.dictionary.field import FieldDefinition


class EPComponent:
    """Composant d'interface construit à partir d'un champ métier."""

    def __init__(self, field: FieldDefinition) -> None:
        self._field = field

    @property
    def field(self) -> FieldDefinition:
        return self._field

    @property
    def name(self) -> str:
        return self._field.name