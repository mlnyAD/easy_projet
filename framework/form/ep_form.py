

from __future__ import annotations

from framework.form.form_definition import FormDefinition
from framework.dictionary.field import FieldDefinition
from framework.components.factory import ComponentFactory


class EPForm:
    MODE_CREATE = "create"
    MODE_EDIT = "edit"
    MODE_READONLY = "readonly"

    def __init__(
        self,
        definition,
        *,
        mode=MODE_CREATE,
        **kwargs,
    ):
        self.definition = definition
        self.mode = mode

    @property
    def is_readonly(self):
        return self.mode == self.MODE_READONLY
    
    @property
    def definition(self) -> FormDefinition:
        return self._definition

    @property
    def entity(self):
        return self._definition.entity

    @property
    def fields(self) -> list[FieldDefinition]:
        return self._definition.fields