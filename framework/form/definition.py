

from dataclasses import dataclass, field

from framework.form.collection import (
    FormCollectionDefinition,
)
from framework.form.field import FieldDefinition
from framework.form.section import SectionDefinition


@dataclass(frozen=True, slots=True)
class FormDefinition:
    """
    Décrit complètement un formulaire.
    """

    name: str
    title: str

    sections: list[SectionDefinition] = field(
        default_factory=list
    )

    collections: list[
        FormCollectionDefinition
    ] = field(
        default_factory=list
    )

    def get_field(
        self,
        name: str,
    ) -> FieldDefinition | None:
        """
        Retourne le champ correspondant au nom fourni.
        """

        for section in self.sections:
            for field_definition in section.fields:
                if field_definition.name == name:
                    return field_definition

        return None

    def get_collection(
        self,
        name: str,
    ) -> FormCollectionDefinition | None:
        """
        Retourne la collection correspondant au nom fourni.
        """

        for collection in self.collections:
            if collection.name == name:
                return collection

        return None