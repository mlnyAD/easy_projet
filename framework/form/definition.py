

from dataclasses import dataclass, field

from framework.form.field import FieldDefinition
from framework.form.section import SectionDefinition


@dataclass(frozen=True, slots=True)
class FormDefinition:
    """
    Décrit complètement un formulaire.
    """

    name: str
    title: str
    sections: list[SectionDefinition] = field(default_factory=list)

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