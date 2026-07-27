

"""
Registre des fournisseurs de choix.
"""

from framework.providers.provider import ChoiceProvider


class ProviderRegistry:
    """Registre des fournisseurs de choix."""

    def __init__(self) -> None:
        self._providers: dict[str, ChoiceProvider] = {}

    def register(
        self,
        name: str,
        provider: ChoiceProvider,
    ) -> None:
        """Enregistre un fournisseur."""

        self._providers[name] = provider

    def get(
        self,
        name: str,
    ) -> ChoiceProvider:
        """Retourne un fournisseur."""

        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown provider '{name}'."
            ) from exc