

"""
Définition d'un fournisseur de choix.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChoiceProviderDefinition:
    """
    Décrit comment obtenir une liste de choix.

    Exemple :
        ChoiceProviderDefinition(
            provider="catalog",
            source="COMPANY_TYPE",
        )
    """

    provider: str
    source: str | None = None