

"""
Tags de template des boutons Easy Projet.

Ce module assure la liaison entre EPButton et le Design System EDF.

Il ne contient :
- aucune règle métier ;
- aucune règle CSS ;
- aucune classe Tailwind.

La présentation visuelle est entièrement définie dans :

    static/src/edf/buttons.css
"""

from __future__ import annotations

from django import template

from framework.button import (
    ButtonAction,
    ButtonDefinition,
    ButtonType,
    EPButton,
)


register = template.Library()


def _resolve_action(
    action: ButtonAction | str,
) -> ButtonAction:
    """
    Normalise l'action fonctionnelle du bouton.
    """

    if isinstance(action, ButtonAction):
        return action

    return ButtonAction(action)


def _resolve_button_type(
    button_type: ButtonType | str,
) -> ButtonType:
    """
    Normalise le type HTML du bouton.
    """

    if isinstance(button_type, ButtonType):
        return button_type

    return ButtonType(button_type)


@register.inclusion_tag(
    "edf/components/button.html"
)
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
    - execute ;
    - cancel ;
    - danger.

    La présentation correspondant à cette intention est gérée
    exclusivement par le CSS EDF.
    """

    resolved_action = _resolve_action(
        action
    )

    resolved_button_type = (
        _resolve_button_type(
            button_type
        )
    )

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

    return {
        "button": button,
    }