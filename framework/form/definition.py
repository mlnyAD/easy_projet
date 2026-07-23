

from dataclasses import dataclass, field

from framework.form.section import SectionDefinition


@dataclass(frozen=True, slots=True)
class FormDefinition:
    """
    Décrit complètement un formulaire.
    """

    name: str

    title: str

    sections: list[SectionDefinition] = field(default_factory=list)