

from enum import Enum


class FormMode(Enum):
    """
    Modes d'ouverture d'un formulaire.
    """

    CREATE = "create"
    EDIT = "edit"
    READONLY = "readonly"