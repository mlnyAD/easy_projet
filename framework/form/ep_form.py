

from __future__ import annotations

from framework.form.form_definition import FormDefinition
from framework.dictionary.field import FieldDefinition


class EPForm:
    """Formulaire métier prêt à être exploité par un renderer."""

    def __init__(self, definition: FormDefinition) -> None:
        self._definition = definition

    @property
    def definition(self) -> FormDefinition:
        return self._definition

    @property
    def entity(self):
        return self._definition.entity

    @property
    def fields(self) -> list[FieldDefinition]:
        return self._definition.fields