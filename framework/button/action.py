

from enum import StrEnum


class ButtonAction(StrEnum):
    """
    Actions fonctionnelles supportées par EPButton.
    """

    EXECUTE = "execute"

    CANCEL = "cancel"

    DANGER = "danger"