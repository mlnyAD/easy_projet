

from dataclasses import dataclass, field

from framework.form.section import SectionDefinition
from framework.form.field import FieldDefinition
from framework.form.field import FieldDefinition


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
            for field in section.fields:
                if field.name == name:
                    return field

        return None