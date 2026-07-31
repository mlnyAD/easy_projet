

from __future__ import annotations

from django import template

from common.ui.css import COLUMN_WIDTH_CLASSES
from framework.viewmodel.column import ViewColumn
from common.ui.css import (
    COLUMN_ALIGNMENT_CLASSES,
    COLUMN_WIDTH_CLASSES,
)

register = template.Library()


@register.filter
def column_width_class(column: object) -> str:
    """
    Retourne les classes Tailwind correspondant à la largeur
    sémantique d'une colonne.
    """
    if not isinstance(column, ViewColumn):
        return ""

    return COLUMN_WIDTH_CLASSES.get(column.width, "")

@register.filter
def column_alignment_class(column: object) -> str:
    """
    Retourne la classe CSS correspondant à l'alignement.
    """
    if not isinstance(column, ViewColumn):
        return ""

    return COLUMN_ALIGNMENT_CLASSES.get(column.align, "")