

from dataclasses import dataclass, field

from framework.form.field import FieldDefinition


@dataclass(frozen=True, slots=True)
class SectionDefinition:
    """
    Décrit une section d'un formulaire.
    """

    title: str

    fields: list[FieldDefinition] = field(default_factory=list)