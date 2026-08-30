

"""
Champ de formulaire prêt à être affiché.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.forms.boundfield import BoundField

from framework.form.field import FieldDefinition
from framework.form.file_upload import FileUploadDefinition
from framework.form.kinds import FieldKind


@dataclass(frozen=True, slots=True)
class ResolvedField:
    """
    Associe une définition de champ Easy Projet à son BoundField Django.
    """

    definition: FieldDefinition
    bound_field: BoundField

    def __post_init__(self) -> None:
        if not isinstance(self.definition, FieldDefinition):
            raise TypeError(
                "La propriété 'definition' doit être une instance "
                "de FieldDefinition."
            )

        if not isinstance(self.bound_field, BoundField):
            raise TypeError(
                "La propriété 'bound_field' doit être une instance "
                "de BoundField."
            )

    @property
    def name(self) -> str:
        """Retourne le nom du champ."""
        return self.definition.name

    @property
    def kind(self) -> FieldKind:
        """Retourne le type sémantique du champ."""
        return self.definition.kind

    @property
    def label(self) -> str:
        """
        Retourne le libellé déclaré ou le libellé fourni par Django.
        """
        if self.definition.label is not None:
            return self.definition.label

        return self.bound_field.label

    @property
    def help_text(self) -> str:
        """
        Retourne l'aide déclarée ou l'aide fournie par Django.
        """
        if self.definition.help_text is not None:
            return self.definition.help_text

        return self.bound_field.help_text

    @property
    def required(self) -> bool:
        """Indique si le champ est obligatoire."""
        return self.definition.required

    @property
    def readonly(self) -> bool:
        """Indique si le champ est en lecture seule."""
        return self.definition.readonly

    @property
    def disabled(self) -> bool:
        """Indique si le champ est désactivé."""
        return self.definition.disabled

    @property
    def checked_label(self) -> str:
        """Retourne le libellé associé à l'état coché."""
        return self.definition.checked_label

    @property
    def unchecked_label(self) -> str:
        """Retourne le libellé associé à l'état non coché."""
        return self.definition.unchecked_label

    @property
    def upload(self) -> FileUploadDefinition | None:
        """
        Retourne la configuration d'import du champ.
        """
        return self.definition.upload

    @property
    def is_file_upload(self) -> bool:
        """
        Indique si le champ utilise le composant FileUpload.
        """
        return self.kind == FieldKind.FILE_UPLOAD

    @property
    def errors(self):
        """Retourne les erreurs Django du champ."""
        return self.bound_field.errors

    @property
    def value(self):
        """Retourne la valeur courante du champ."""
        return self.bound_field.value()

    @property
    def id_for_label(self) -> str:
        """Retourne l'identifiant HTML associé au libellé."""
        return self.bound_field.id_for_label

    @property
    def catalog_code(self) -> str | None:
        """Retourne le code du catalogue associé au champ."""
        return getattr(
            self.bound_field.field,
            "catalog_code",
            None,
        )

    @property
    def catalog_is_editable(self) -> bool:
        """Indique si le catalogue peut être modifié."""
        return bool(
            getattr(
                self.bound_field.field,
                "catalog_is_editable",
                False,
            )
        )

    @property
    def catalog_is_incremental(self) -> bool:
        """Indique si une valeur peut être ajoutée depuis le champ."""
        return bool(
            getattr(
                self.bound_field.field,
                "catalog_is_incremental",
                False,
            )
        )

    @property
    def allows_catalog_increment(self) -> bool:
        """
        Indique si le champ autorise l'ajout direct d'une valeur.
        """
        return (
            self.catalog_is_editable
            and self.catalog_is_incremental
        )