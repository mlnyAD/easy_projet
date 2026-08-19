

from django import template

from apps.reporting.permissions import (
    can_review_activity_reports,
)


register = template.Library()


@register.simple_tag
def can_review_reports(user) -> bool:
    """
    Indique si l'utilisateur peut accéder
    à la validation des rapports d'activité.
    """

    return can_review_activity_reports(user)