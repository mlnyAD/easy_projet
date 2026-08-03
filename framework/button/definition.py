

from __future__ import annotations

from dataclasses import dataclass

from framework.button.action import ButtonAction
from framework.button.type import ButtonType
from framework.defaults.button import (
    DEFAULT_BUTTON_ACTION,
    DEFAULT_BUTTON_CONFIRM,
    DEFAULT_BUTTON_DISABLED,
    DEFAULT_BUTTON_ICON,
    DEFAULT_BUTTON_TYPE,
)


@dataclass(frozen=True, slots=True)
class ButtonDefinition:
    """
    Décrit un bouton du framework.

    Cette classe est indépendante de Django, du HTML et du Design System.
    """

    label: str

    action: ButtonAction = DEFAULT_BUTTON_ACTION

    url: str | None = None

    button_type: ButtonType = DEFAULT_BUTTON_TYPE

    icon: str | None = DEFAULT_BUTTON_ICON

    disabled: bool = DEFAULT_BUTTON_DISABLED

    confirm: str | None = DEFAULT_BUTTON_CONFIRM