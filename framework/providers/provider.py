

"""
Contrats des fournisseurs de choix du framework.
"""

from abc import ABC
from abc import abstractmethod

from framework.context import EPContext

from .choice import Choice
from .definition import ChoiceProviderDefinition


class ChoiceProvider(ABC):
    """Contrat abstrait d'un fournisseur de choix."""

    @abstractmethod
    def get_choices(
        self,
        definition: ChoiceProviderDefinition,
        context: EPContext,
    ) -> list[Choice]:
        """Retourne les choix disponibles."""
        raise NotImplementedError