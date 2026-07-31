

"""
Comportements communs aux vues Easy Projet.
"""

from framework.context.context import EPContext
from framework.providers import ProviderRegistry


class EPViewMixin:
    """
    Fonctionnalités communes aux vues du framework.
    """

    cancel_url = None

    def get_ep_context(self) -> EPContext:
        """
        Retourne le contexte d'exécution.

        Cette première implémentation est volontairement minimale.
        Elle sera enrichie lorsque l'authentification et les projets
        seront opérationnels.
        """

        return EPContext(
            operator=None,
            client_environment=None,
            company=None,
            project=None,
        )

    def get_provider_registry(self) -> ProviderRegistry:
        """
        Retourne le registre des fournisseurs de choix.
        """

        return ProviderRegistry()
    
    def get_cancel_url(self):
        if self.cancel_url is not None:
            return str(self.cancel_url)

        if getattr(self, "success_url", None) is not None:
            return str(self.success_url)

        return None