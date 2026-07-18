

"""
Tags de template du Design System Easy Projet.

Ce module assure la liaison entre les champs Django et les composants
graphiques Easy Projet.

Il ne doit contenir aucune règle métier.
"""

from django import forms, template

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

    Les chaînes absentes ou vides sont ignorées.
    """
    return " ".join(
        css_class.strip()
        for css_class in classes
        if css_class and css_class.strip()
    )


def _get_input_state_classes(field) -> str:
    """
    Retourne les classes correspondant à l'état du champ.
    """
    if field.errors:
        return INPUT_ERROR_CLASSES

    return INPUT_NORMAL_CLASSES


def _build_aria_describedby(field) -> str:
    """
    Construit la liste des éléments décrivant le champ.

    La liste peut référencer :

    - l'aide associée au champ ;
    - les erreurs de validation associées au champ.
    """
    if not field.auto_id:
        return ""

    described_by = []

    if field.help_text:
        described_by.append(f"{field.auto_id}_help")

    if field.errors:
        described_by.append(f"{field.auto_id}_errors")

    return " ".join(described_by)


def _build_common_attributes(field, css_classes: str) -> dict[str, str]:
    """
    Construit les attributs HTML communs aux widgets Easy Projet.
    """
    attrs = {
        "class": css_classes,
    }

    aria_describedby = _build_aria_describedby(field)

    if aria_describedby:
        attrs["aria-describedby"] = aria_describedby

    if field.errors:
        attrs["aria-invalid"] = "true"

    return attrs


def _build_input_context(field) -> dict:
    """
    Construit le contexte commun aux composants de saisie textuelle.

    Cette fonction centralise :

    - les classes CSS du widget ;
    - l'état normal ou en erreur ;
    - les attributs ARIA.
    """
    widget = field.field.widget
    existing_classes = widget.attrs.get("class", "")

    css_classes = _join_classes(
        existing_classes,
        INPUT_BASE_CLASSES,
        _get_input_state_classes(field),
    )

    return {
        "field": field,
        "css_classes": css_classes,
        "aria_describedby": _build_aria_describedby(field),
        "aria_invalid": bool(field.errors),
    }


@register.inclusion_tag("components/forms/ep_text_input.html")
def ep_text_input(field):
    """
    Rend un composant TextInput Easy Projet à partir d'un BoundField Django.

    Le composant est réservé au widget forms.TextInput standard.
    Les widgets spécialisés disposent de leur propre composant.
    """
    widget = field.field.widget

    if not isinstance(widget, forms.TextInput):
        raise TypeError(
            "ep_text_input attend un champ utilisant un widget "
            "dérivé de django.forms.TextInput."
        )

    if isinstance(widget, forms.EmailInput):
        raise TypeError(
            "ep_text_input ne doit pas être utilisé avec forms.EmailInput. "
            "Utiliser ep_email_input."
        )

    return _build_input_context(field)


@register.inclusion_tag("components/forms/ep_email_input.html")
def ep_email_input(field):
    """
    Rend un composant EmailInput Easy Projet à partir d'un BoundField Django.

    Le composant assure uniquement le rendu d'un champ HTML de type email.
    La validation serveur reste assurée par Django.
    """
    widget = field.field.widget

    if not isinstance(widget, forms.EmailInput):
        raise TypeError(
            "ep_email_input attend un champ utilisant "
            "django.forms.EmailInput."
        )

    return _build_input_context(field)


@register.simple_tag
def ep_widget(field):
    """
    Rend les widgets qui ne disposent pas encore d'un composant spécialisé.

    Ce mécanisme constitue un fallback temporaire. Il sera progressivement
    remplacé par les futurs composants du Design System Easy Projet.
    """
    widget = field.field.widget
    existing_classes = widget.attrs.get("class", "")

    if isinstance(widget, forms.CheckboxInput):
        component_classes = CHECKBOX_CLASSES
    else:
        component_classes = _join_classes(
            INPUT_BASE_CLASSES,
            _get_input_state_classes(field),
        )

    css_classes = _join_classes(
        existing_classes,
        component_classes,
    )

    attrs = _build_common_attributes(
        field=field,
        css_classes=css_classes,
    )

    return field.as_widget(attrs=attrs)