

"""
Formulaire générique du framework Easy Projet.
"""

from dataclasses import dataclass

from framework.context import EPContext
from framework.form.definition import FormDefinition
from framework.providers import ProviderRegistry

from framework.form.field import FieldDefinition
from framework.providers import Choice


@dataclass(frozen=True, slots=True)
class EPForm:
    """
    Représente un formulaire générique Easy Projet.

    EPForm orchestre une définition de formulaire, un contexte
    d'exécution et un registre de fournisseurs.

    Il ne produit pas directement de HTML et ne dépend pas de Django.
    """

    definition: FormDefinition
    context: EPContext
    providers: ProviderRegistry
    
    @property
    def title(self) -> str:
        """
        Retourne le titre du formulaire.
        """
        return self.definition.title

    @property
    def sections(self):
        """
        Retourne les sections du formulaire.
        """
        return self.definition.sections
    
    def get_choices(
        self,
        field: FieldDefinition,
    ) -> list[Choice]:
        """
        Retourne les choix disponibles pour un champ.
        """

        if field.provider is None:
            return []

        provider = self.providers.get(
            field.provider.provider,
        )

        return provider.get_choices(
            field.provider,
            self.context,
        )