

from framework.button.action import ButtonAction
from framework.button.definition import ButtonDefinition
from framework.button.type import ButtonType


class ButtonValidationError(ValueError):
    """Erreur de validation d'un bouton."""


class ButtonValidator:
    """Valide une définition de bouton."""

    def validate(self, definition: ButtonDefinition) -> None:
        if not isinstance(definition, ButtonDefinition):
            raise ButtonValidationError(
                "La définition doit être une instance de ButtonDefinition."
            )

        self._validate_label(definition.label)
        self._validate_action(definition.action)
        self._validate_url(definition.url)
        self._validate_button_type(definition.button_type)
        self._validate_icon(definition.icon)
        self._validate_disabled(definition.disabled)
        self._validate_confirm(definition.confirm)

    def _validate_label(self, label: object) -> None:
        if not isinstance(label, str):
            raise ButtonValidationError(
                "Le libellé doit être une chaîne de caractères."
            )

        if not label.strip():
            raise ButtonValidationError(
                "Le libellé est obligatoire."
            )

    def _validate_action(self, action: object) -> None:
        if not isinstance(action, ButtonAction):
            raise ButtonValidationError(
                "L'action est invalide."
            )

    def _validate_url(self, url: object) -> None:
        if url is None:
            return

        if not isinstance(url, str):
            raise ButtonValidationError(
                "L'URL doit être une chaîne de caractères."
            )

        if not url.strip():
            raise ButtonValidationError(
                "L'URL ne peut pas être vide."
            )

    def _validate_button_type(self, button_type: object) -> None:
        if not isinstance(button_type, ButtonType):
            raise ButtonValidationError(
                "Le type de bouton est invalide."
            )

    def _validate_icon(self, icon: object) -> None:
        if icon is None:
            return

        if not isinstance(icon, str):
            raise ButtonValidationError(
                "L'icône doit être une chaîne de caractères."
            )

        if not icon.strip():
            raise ButtonValidationError(
                "L'icône ne peut pas être vide."
            )

    def _validate_disabled(self, disabled: object) -> None:
        if not isinstance(disabled, bool):
            raise ButtonValidationError(
                "La propriété 'disabled' doit être un booléen."
            )

    def _validate_confirm(self, confirm: object) -> None:
        if confirm is None:
            return

        if not isinstance(confirm, str):
            raise ButtonValidationError(
                "Le message de confirmation doit être une chaîne de caractères."
            )

        if not confirm.strip():
            raise ButtonValidationError(
                "Le message de confirmation ne peut pas être vide."
            )