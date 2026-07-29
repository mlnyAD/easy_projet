

from __future__ import annotations

from framework.components.base.component import EPComponent
from framework.dictionary.field import FieldDefinition


class EPTextInput(EPComponent):
    """Composant de saisie pour une valeur textuelle courte."""

    def __init__(self, field: FieldDefinition) -> None:
        super().__init__(field)

    @property
    def data_type(self) -> str:
        return self.field.data_type