

"""
Tags de template des formulaires Easy Projet.

Ce module assure la liaison entre les BoundField Django et les
composants graphiques du Design System EDF.

Il ne contient :
- aucune règle métier ;
- aucune règle de présentation CSS.

La présentation des widgets est déléguée au WidgetAdapter puis
aux feuilles de style EDF.
"""

from django import template
from django.forms.boundfield import BoundField

from common.forms.widget_registry import (
    get_widget_kind,
    validate_bound_field,
)
from framework.integrations.django.widget_adapter import (
    WidgetAdapter,
)


register = template.Library()

_widget_adapter = WidgetAdapter()


def _build_aria_describedby(
    field: BoundField,
) -> str | None:
    """
    Construit la relation entre le champ et ses informations associées.

    Le widget peut être relié :
    - au texte d'aide ;
    - aux erreurs de validation.
    """

    if not field.auto_id:
        return None

    described_by = []

    if field.help_text:
        described_by.append(
            f"{field.auto_id}_help"
        )

    if field.errors:
        described_by.append(
            f"{field.auto_id}_errors"
        )

    if not described_by:
        return None

    return " ".join(described_by)


def _apply_widget_semantics(
    field: BoundField,
    *,
    widget_kind: str,
) -> None:
    """
    Complète les attributs fonctionnels propres à certains widgets.

    Les attributs ajoutés ici décrivent le comportement HTML.
    Ils ne définissent pas la présentation graphique.
    """

    widget = field.field.widget

    if widget_kind == "email":
        widget.attrs.setdefault(
            "inputmode",
            "email",
        )
        widget.attrs.setdefault(
            "autocomplete",
            "email",
        )

    elif widget_kind == "phone":
        widget.attrs.setdefault(
            "inputmode",
            "tel",
        )
        widget.attrs.setdefault(
            "autocomplete",
            "tel",
        )
        widget.attrs.setdefault(
            "data-phone",
            "",
        )


@register.inclusion_tag(
    "edf/form/ep_form_field.html"
)
def ep_form_field(
    field: BoundField,
) -> dict:
    """
    Rend un champ Django avec le composant EDF approprié.

    Le traitement suit trois étapes :

    1. identification du type de widget ;
    2. adaptation au Design System EDF ;
    3. rendu par le template générique du champ.
    """

    validate_bound_field(field)

    widget_kind = get_widget_kind(
        field
    )

    described_by = (
        _build_aria_describedby(
            field
        )
    )

    _widget_adapter.adapt(
        field.field.widget,
        has_errors=bool(
            field.errors
        ),
        described_by=described_by,
    )

    _apply_widget_semantics(
        field,
        widget_kind=widget_kind,
    )

    return {
        "field": field,
        "widget_kind": widget_kind,
        "widget_html": field.as_widget(),
        "is_checkbox": (
            widget_kind == "checkbox"
        ),
    }