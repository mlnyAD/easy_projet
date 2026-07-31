

from __future__ import annotations

from dataclasses import dataclass
from framework.types.field_width import FieldWidth

from framework.defaults.field import (
    DEFAULT_FIELD_AUTOFOCUS,
    DEFAULT_FIELD_AUTOCOMPLETE,
    DEFAULT_FIELD_ICON,
    DEFAULT_FIELD_PLACEHOLDER,
    DEFAULT_FIELD_TAB_INDEX,
    DEFAULT_FIELD_VISIBLE,
    DEFAULT_FIELD_WIDTH,
)
from framework.form.kinds import FieldKind

from framework.providers import ChoiceProviderDefinition


@dataclass(frozen=True, slots=True)
class FieldDefinition:
    """
    Décrit l'utilisation d'un champ dans un formulaire.
    """

    name: str

    kind: FieldKind = FieldKind.TEXT

    label: str | None = None

    help_text: str | None = None

    required: bool = True

    readonly: bool = False

    disabled: bool = False

    provider: ChoiceProviderDefinition | None = None

    visible: bool = DEFAULT_FIELD_VISIBLE

    width: FieldWidth = DEFAULT_FIELD_WIDTH

    placeholder: str | None = DEFAULT_FIELD_PLACEHOLDER

    autofocus: bool = DEFAULT_FIELD_AUTOFOCUS

    autocomplete: str | None = DEFAULT_FIELD_AUTOCOMPLETE

    tab_index: int | None = DEFAULT_FIELD_TAB_INDEX

    icon: str | None = DEFAULT_FIELD_ICON