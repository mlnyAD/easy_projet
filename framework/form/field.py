

from dataclasses import dataclass

from framework.form.kinds import FieldKind
from framework.providers import ChoiceProviderDefinition

@dataclass(frozen=True, slots=True)
class FieldDefinition:
    """
    Décrit un champ de formulaire.
    """

    name: str

    kind: FieldKind = FieldKind.TEXT

    label: str | None = None

    help_text: str | None = None

    required: bool = True

    readonly: bool = False

    disabled: bool = False

    provider: ChoiceProviderDefinition | None = None