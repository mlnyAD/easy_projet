

"""
Tags de template des formulaires Easy Projet.

Ce module assure la liaison entre les BoundField Django et le
composant graphique générique de formulaire.

Il ne contient aucune règle métier.
"""

from django import template
from django.forms.boundfield import BoundField

from common.forms.widget_registry import (
    get_widget_kind,
    validate_bound_field,
)
from common.ui.css import (
    CHECKBOX_CLASSES,
    INPUT_BASE_CLASSES,
    INPUT_ERROR_CLASSES,
    INPUT_NORMAL_CLASSES,
)

register = template.Library()


def _join_classes(*classes: str) -> str:
    """
    Assemble plusieurs chaînes de classes CSS.
    """
    return " ".join(
        css_class.strip()
        for css_class in classes
        if css_class and css_class.strip()
    )


def _get_input_state_classes(field: BoundField) -> str:
    """
    Retourne les classes correspondant à l'état du champ.
    """
    if field.errors:
        return INPUT_ERROR_CLASSES

    return INPUT_NORMAL_CLASSES


def _build_aria_describedby(field: BoundField) -> str:
    """
    Construit l'attribut aria-describedby du champ.
    """
    if not field.auto_id:
        return ""

    described_by = []

    if field.help_text:
        described_by.append(f"{field.auto_id}_help")

    if field.errors:
        described_by.append(f"{field.auto_id}_errors")

    return " ".join(described_by)


def _build_widget_attributes(
    field: BoundField,
    *,
    widget_kind: str,
) -> dict[str, str]:
    """
    Construit les attributs HTML ajoutés au widget Django.
    """
    existing_classes = field.field.widget.attrs.get("class", "")

    if widget_kind == "checkbox":
        component_classes = CHECKBOX_CLASSES
    else:
        component_classes = _join_classes(
            INPUT_BASE_CLASSES,
            _get_input_state_classes(field),
        )

    attrs = {
        "class": _join_classes(
            existing_classes,
            component_classes,
        ),
    }

    aria_describedby = _build_aria_describedby(field)

    if aria_describedby:
        attrs["aria-describedby"] = aria_describedby

    if field.errors:
        attrs["aria-invalid"] = "true"

    if widget_kind == "email":
        attrs.update(
            {
                "inputmode": "email",
                "autocomplete": "email",
            }
        )

    if widget_kind == "phone":
        attrs.update(
            {
                "inputmode": "tel",
                "autocomplete": "tel",
                "data-phone": "",
            }
        )

    return attrs


@register.inclusion_tag("components/forms/ep_form_field.html")
def ep_form_field(field: BoundField) -> dict:
    """
    Rend un champ Django avec le composant Easy Projet approprié.
    """
    validate_bound_field(field)

    widget_kind = get_widget_kind(field)

    attrs = _build_widget_attributes(
        field,
        widget_kind=widget_kind,
    )

    return {
        "field": field,
        "widget_kind": widget_kind,
        "widget_html": field.as_widget(attrs=attrs),
        "is_checkbox": widget_kind == "checkbox",
    }