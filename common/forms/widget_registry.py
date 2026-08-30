

"""
Registre des widgets de formulaire Easy Projet.

Ce module identifie la nature graphique d'un champ Django.
Il ne contient aucune règle métier ni aucun rendu HTML.
"""

from typing import Literal

from django import forms
from django.forms.boundfield import BoundField

from common.forms.widgets import (
    FileUploadInput,
    TelInput,
)


WidgetKind = Literal[
    "checkbox",
    "email",
    "phone",
    "text",
    "textarea",
    "select",
    "file",
    "default",
]


def validate_bound_field(field: BoundField) -> None:
    """
    Vérifie que le composant reçoit bien un champ lié Django.
    """

    if not isinstance(field, BoundField):
        raise TypeError(
            "Le composant de formulaire attend un "
            "django.forms.boundfield.BoundField."
        )


def get_widget_kind(field: BoundField) -> WidgetKind:
    """
    Retourne le type de composant correspondant au widget Django.
    """

    validate_bound_field(field)

    widget = field.field.widget

    if isinstance(
        widget,
        forms.CheckboxInput,
    ):
        return "checkbox"

    if isinstance(
        widget,
        forms.EmailInput,
    ):
        return "email"

    if (
        isinstance(widget, TelInput)
        or (
            isinstance(
                widget,
                forms.TextInput,
            )
            and getattr(
                widget,
                "input_type",
                None,
            ) == "tel"
        )
    ):
        return "phone"

    if isinstance(
        widget,
        forms.Textarea,
    ):
        return "textarea"

    if isinstance(
        widget,
        forms.Select,
    ):
        return "select"

    if isinstance(
        widget,
        FileUploadInput,
    ):
        return "file"

    if isinstance(
        widget,
        forms.TextInput,
    ):
        return "text"

    return "default"