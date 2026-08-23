

from __future__ import annotations

from .base import DocumentIntegration


class DocumentIntegrationRegistry:
    """
    Registre des intégrations documentaires disponibles.
    """

    def __init__(self) -> None:
        self._integrations: dict[
            str,
            DocumentIntegration,
        ] = {}

    def register(
        self,
        integration: DocumentIntegration,
    ) -> None:
        provider_code = (
            integration.provider_code
            .strip()
            .upper()
        )

        if not provider_code:
            raise ValueError(
                "Le code fournisseur ne peut pas être vide."
            )

        if provider_code in self._integrations:
            raise ValueError(
                f"Intégration déjà enregistrée : "
                f"{provider_code}"
            )

        self._integrations[
            provider_code
        ] = integration

    def get(
        self,
        provider_code: str,
    ) -> DocumentIntegration:
        key = (
            provider_code
            .strip()
            .upper()
        )

        try:
            return self._integrations[key]
        except KeyError as exc:
            raise LookupError(
                f"Intégration inconnue : {provider_code}"
            ) from exc

    def all(
        self,
    ) -> tuple[DocumentIntegration, ...]:
        return tuple(
            self._integrations.values()
        )

    def clear(self) -> None:
        """
        Principalement utile pour les tests.
        """

        self._integrations.clear()


registry = DocumentIntegrationRegistry()