

"""
Tags de template des boutons Easy Projet.

Ce module assure la liaison entre EPButton et le Design System.
Il ne contient aucune règle métier.
"""

from __future__ import annotations

from django import template

from common.ui.buttons import (
    BUTTON_BASE_CLASSES,
    BUTTON_CANCEL_CLASSES,
    BUTTON_DANGER_CLASSES,
    BUTTON_EXECUTE_CLASSES,
)
from framework.button import (
    ButtonAction,
    ButtonDefinition,
    ButtonType,
    EPButton,
)


register = template.Library()


BUTTON_ACTION_CLASSES = {
    ButtonAction.EXECUTE: BUTTON_EXECUTE_CLASSES,
    ButtonAction.CANCEL: BUTTON_CANCEL_CLASSES,
    ButtonAction.DANGER: BUTTON_DANGER_CLASSES,
}


def _join_classes(*classes: str) -> str:
    """Assemble plusieurs chaînes de classes CSS."""
    return " ".join(
        css_class.strip()
        for css_class in classes
        if css_class and css_class.strip()
    )


def _resolve_action(
    action: ButtonAction | str,
) -> ButtonAction:
    if isinstance(action, ButtonAction):
        return action

    return ButtonAction(action)


def _resolve_button_type(
    button_type: ButtonType | str,
) -> ButtonType:
    if isinstance(button_type, ButtonType):
        return button_type

    return ButtonType(button_type)


@register.inclusion_tag("edf/components/button.html")
def ep_button(
    *,
    label: str,
    action: ButtonAction | str = ButtonAction.EXECUTE,
    url: str | None = None,
    button_type: ButtonType | str = ButtonType.BUTTON,
    icon: str | None = None,
    disabled: bool = False,
    confirm: str | None = None,
) -> dict:
    """
    Rend un bouton du Design System Easy Projet.

    Le paramètre action décrit l'intention fonctionnelle :
    execute, cancel ou danger.
    """
    resolved_action = _resolve_action(action)
    resolved_button_type = _resolve_button_type(button_type)

    button = EPButton(
        definition=ButtonDefinition(
            label=label,
            action=resolved_action,
            url=url,
            button_type=resolved_button_type,
            icon=icon,
            disabled=disabled,
            confirm=confirm,
        ),
    )

    action_classes = BUTTON_ACTION_CLASSES[button.action]

    css_classes = _join_classes(
        BUTTON_BASE_CLASSES,
        action_classes,
        "pointer-events-none opacity-50"
        if button.disabled and button.is_link
        else "",
    )

    return {
        "button": button,
        "css_classes": css_classes,
    }