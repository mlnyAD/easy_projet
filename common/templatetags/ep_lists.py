

"""
Tags de template des listes Easy Projet.

Ce module assure la liaison entre les propriétés sémantiques
des colonnes du framework et les classes du Design System EDF.

Il ne contient aucune règle métier ni aucune règle de
présentation détaillée.

La présentation correspondante est définie dans :

    static/src/edf/lists.css
"""

from __future__ import annotations

from django import template

from framework.viewmodel.column import ViewColumn


register = template.Library()


# ---------------------------------------------------------------------------
# Correspondance entre les propriétés sémantiques du framework
# et les composants CSS EDF.
#
# La largeur réelle en pixels/rem reste exclusivement définie
# dans static/src/edf/lists.css.
# ---------------------------------------------------------------------------

COLUMN_WIDTH_CLASSES = {
    "auto": "",
    "xs": "ep-col-width-xs",
    "s": "ep-col-width-s",
    "sm": "ep-col-width-sm",
    "md": "ep-col-width-md",
    "lg": "ep-col-width-lg",
    "xl": "ep-col-width-xl",
}


COLUMN_ALIGNMENT_CLASSES = {
    "left": "ep-align-left",
    "center": "ep-align-center",
    "right": "ep-align-right",
}


@register.filter
def column_width_class(
    column: object,
) -> str:
    """
    Retourne la classe EDF correspondant à la largeur
    sémantique d'une colonne.
    """

    if not isinstance(
        column,
        ViewColumn,
    ):
        return ""

    return COLUMN_WIDTH_CLASSES.get(
        column.width,
        "",
    )


@register.filter
def column_alignment_class(
    column: object,
) -> str:
    """
    Retourne la classe EDF correspondant à l'alignement
    sémantique d'une colonne.
    """

    if not isinstance(
        column,
        ViewColumn,
    ):
        return ""

    return COLUMN_ALIGNMENT_CLASSES.get(
        column.align,
        "",
    )