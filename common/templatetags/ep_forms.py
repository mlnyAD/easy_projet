

"""
Tags de template des composants de formulaire Easy Projet.

Ce module assure la liaison entre les champs Django et les composants
graphiques de l'application.

Responsabilités :
    - contrôler le type de widget attendu par chaque composant ;
    - construire les classes CSS des widgets ;
    - construire les attributs d'accessibilité ;
    - rendre les widgets Django dans les composants spécialisés.

Ce module ne contient aucune règle métier.
"""

from django import forms, template

from common.ui.css import (
    CHECKBOX_CLASSES,
    INPUT_BASE_CLASSES,
    INPUT_ERROR_CLASSES,
    INPUT_NORMAL_CLASSES,
)

register = template.Library()


# =============================================================================
# Utilitaires internes
# =============================================================================


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
    Retourne les classes CSS correspondant à l'état du champ.
    """
    if field.errors:
        return INPUT_ERROR_CLASSES

    return INPUT_NORMAL_CLASSES


def _build_aria_describedby(field) -> str:
    """
    Construit la valeur de l'attribut aria-describedby.

    Le champ peut être décrit par son texte d'aide et par ses erreurs.
    """
    if not field.auto_id:
        return ""

    described_by = []

    if field.help_text:
        described_by.append(f"{field.auto_id}_help")

    if field.errors:
        described_by.append(f"{field.auto_id}_errors")

    return " ".join(described_by)


def _build_common_attributes(
    field,
    css_classes: str,
) -> dict[str, str]:
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


# =============================================================================
# Construction des contextes
# =============================================================================


def _build_component_context(
    field,
    *,
    component_classes: str,
    include_input_state: bool = False,
    additional_attrs: dict[str, str] | None = None,
) -> dict:
    """
    Construit le contexte commun d'un composant de formulaire.

    Les attributs déjà définis sur le widget Django sont conservés par
    field.as_widget().

    additional_attrs permet au composant d'ajouter quelques attributs
    strictement liés à son comportement d'interface.
    """
    widget = field.field.widget
    existing_classes = widget.attrs.get("class", "")

    state_classes = ""

    if include_input_state:
        state_classes = _get_input_state_classes(field)

    css_classes = _join_classes(
        existing_classes,
        component_classes,
        state_classes,
    )

    attrs = _build_common_attributes(
        field=field,
        css_classes=css_classes,
    )

    if additional_attrs:
        attrs.update(additional_attrs)

    return {
        "field": field,
        "widget_html": field.as_widget(attrs=attrs),
    }


def _build_input_context(
    field,
    *,
    additional_attrs: dict[str, str] | None = None,
) -> dict:
    """
    Construit le contexte commun des composants de saisie.
    """
    return _build_component_context(
        field,
        component_classes=INPUT_BASE_CLASSES,
        include_input_state=True,
        additional_attrs=additional_attrs,
    )


def _build_checkbox_context(field) -> dict:
    """
    Construit le contexte du composant Checkbox.
    """
    return _build_component_context(
        field,
        component_classes=CHECKBOX_CLASSES,
    )


# =============================================================================
# Contrôles des widgets
# =============================================================================


def _is_phone_widget(widget) -> bool:
    """
    Indique si le widget est configuré comme champ téléphonique.
    """
    return (
        isinstance(widget, forms.TextInput)
        and getattr(widget, "input_type", None) == "tel"
    )


# =============================================================================
# Composants publics
# =============================================================================


@register.inclusion_tag("components/forms/ep_text_input.html")
def ep_text_input(field):
    """
    Rend un composant TextInput Easy Projet.
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

    if _is_phone_widget(widget):
        raise TypeError(
            "ep_text_input ne doit pas être utilisé avec un champ téléphone. "
            "Utiliser ep_phone_input."
        )

    return _build_input_context(field)


@register.inclusion_tag("components/forms/ep_email_input.html")
def ep_email_input(field):
    """
    Rend un composant EmailInput Easy Projet.
    """
    widget = field.field.widget

    if not isinstance(widget, forms.EmailInput):
        raise TypeError(
            "ep_email_input attend un champ utilisant "
            "django.forms.EmailInput."
        )

    return _build_input_context(
        field,
        additional_attrs={
            "inputmode": "email",
            "autocomplete": "email",
        },
    )


@register.inclusion_tag("components/forms/ep_phone_input.html")
def ep_phone_input(field):
    """
    Rend un composant PhoneInput Easy Projet.

    Le widget doit être un TextInput dont le type HTML est « tel ».
    Le formatage côté navigateur reste une aide à la saisie.
    La validation définitive reste assurée par Django.
    """
    widget = field.field.widget

    if not _is_phone_widget(widget):
        raise TypeError(
            "ep_phone_input attend un forms.TextInput configuré "
            'avec attrs={"type": "tel"}.'
        )

    return _build_input_context(
        field,
        additional_attrs={
            "inputmode": "tel",
            "autocomplete": "tel",
            "data-phone": "",
        },
    )


@register.inclusion_tag("components/forms/ep_checkbox.html")
def ep_checkbox(field):
    """
    Rend un composant Checkbox Easy Projet.
    """
    widget = field.field.widget

    if not isinstance(widget, forms.CheckboxInput):
        raise TypeError(
            "ep_checkbox attend un champ utilisant "
            "django.forms.CheckboxInput."
        )

    return _build_checkbox_context(field)


# =============================================================================
# Rendu temporaire des widgets non spécialisés
# =============================================================================


@register.simple_tag
def ep_widget(field):
    """
    Rend un widget ne disposant pas encore d'un composant spécialisé.
    """
    context = _build_input_context(field)

    return context["widget_html"]