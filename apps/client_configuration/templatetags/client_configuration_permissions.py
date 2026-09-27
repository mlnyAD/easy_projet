

from django import template

from ..services.access import (
    ClientConfigurationAccessService,
)


register = template.Library()


@register.simple_tag
def can_manage_client_configuration(
    user,
) -> bool:
    """
    Indique si l'utilisateur dispose d'au moins un environnement
    client qu'il peut administrer.
    """

    return (
        ClientConfigurationAccessService
        .get_manageable_client_environments(
            user
        )
        .exists()
    )