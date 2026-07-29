

from __future__ import annotations

from framework.components.base.component import EPComponent
from framework.components.inputs.text import EPTextInput
from framework.dictionary.field import FieldDefinition


class ComponentFactory:
    """Fabrique des composants à partir d'un champ métier."""

    @classmethod
    def create(cls, field: FieldDefinition) -> EPComponent:
        if field.data_type == "string":
            return EPTextInput(field)

        return EPComponent(field)