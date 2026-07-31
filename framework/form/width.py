

from enum import StrEnum


class FieldWidth(StrEnum):
    """
    Largeurs sémantiques des champs.

    Le Design System est responsable de la traduction
    en classes CSS.
    """

    AUTO = "auto"

    XS = "xs"

    SM = "sm"

    MD = "md"

    LG = "lg"

    XL = "xl"

    FULL = "full"