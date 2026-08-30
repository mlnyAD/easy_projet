

from __future__ import annotations

from dataclasses import dataclass

from framework.defaults.field import (
    DEFAULT_FIELD_AUTOFOCUS,
    DEFAULT_FIELD_AUTOCOMPLETE,
    DEFAULT_FIELD_CHECKED_LABEL,
    DEFAULT_FIELD_ICON,
    DEFAULT_FIELD_PLACEHOLDER,
    DEFAULT_FIELD_TAB_INDEX,
    DEFAULT_FIELD_UNCHECKED_LABEL,
    DEFAULT_FIELD_VISIBLE,
    DEFAULT_FIELD_WIDTH,
)
from framework.form.file_upload import FileUploadDefinition
from framework.form.kinds import FieldKind
from framework.providers import ChoiceProviderDefinition
from framework.types.field_width import FieldWidth


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

    checked_label: str = DEFAULT_FIELD_CHECKED_LABEL

    unchecked_label: str = DEFAULT_FIELD_UNCHECKED_LABEL

    upload: FileUploadDefinition | None = None

    def __post_init__(self) -> None:
        """
        Valide uniquement les règles spécifiques
        à la configuration FileUpload.

        Les validations générales des champs restent
        sous la responsabilité de FormValidator.
        """

        if self.upload is not None and not isinstance(
            self.upload,
            FileUploadDefinition,
        ):
            raise TypeError(
                "La propriété 'upload' doit être une instance "
                "de FileUploadDefinition."
            )

        if (
            self.kind == FieldKind.FILE_UPLOAD
            and self.upload is None
        ):
            raise ValueError(
                "Un champ FILE_UPLOAD doit définir une "
                "configuration 'upload'."
            )

        if (
            self.kind != FieldKind.FILE_UPLOAD
            and self.upload is not None
        ):
            raise ValueError(
                "La propriété 'upload' n'est autorisée "
                "que pour les champs FILE_UPLOAD."
            )