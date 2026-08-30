

from enum import StrEnum


class FieldKind(StrEnum):
    """
    Types de champs supportés par le framework.
    """

    TEXT = "text"

    EMAIL = "email"

    PHONE = "phone"

    TEXTAREA = "textarea"

    SELECT = "select"

    CHECKBOX = "checkbox"

    FILE_UPLOAD = "file_upload"