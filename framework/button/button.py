

from __future__ import annotations

from dataclasses import dataclass

from framework.button.definition import ButtonDefinition
from framework.button.validator import ButtonValidator


@dataclass(frozen=True, slots=True)
class EPButton:
    """
    Représente un bouton prêt à être exploité par une intégration.

    EPButton valide la définition reçue et expose ses propriétés
    sans dépendre de Django, du HTML ou du Design System.
    """

    definition: ButtonDefinition

    def __post_init__(self) -> None:

        if not isinstance(
            self.definition,
            ButtonDefinition,
        ):
            raise TypeError(
                "La propriété 'definition' doit être une instance "
                "de ButtonDefinition."
            )

        ButtonValidator().validate(
            self.definition,
        )

    @property
    def label(self) -> str:
        return self.definition.label

    @property
    def action(self):
        return self.definition.action

    @property
    def url(self) -> str | None:
        return self.definition.url

    @property
    def button_type(self):
        return self.definition.button_type

    @property
    def icon(self) -> str | None:
        return self.definition.icon

    @property
    def disabled(self) -> bool:
        return self.definition.disabled

    @property
    def confirm(self) -> str | None:
        return self.definition.confirm

    @property
    def is_link(self) -> bool:
        return self.url is not None