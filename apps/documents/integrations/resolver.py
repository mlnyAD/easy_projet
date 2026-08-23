

from __future__ import annotations

from apps.documents.models import DocumentVersion
from apps.integrations.models import ExternalIntegration

from .base import DocumentIntegration
from .capabilities import DocumentCapability
from .registry import (
    DocumentIntegrationRegistry,
    registry,
)


CAPABILITY_SERVICE_TYPE = {
    DocumentCapability.OFFICE_EDIT: "OFFICE",
    DocumentCapability.OFFICE_VIEW: "OFFICE",
    DocumentCapability.CAD_VIEW: "CAD_VIEWER",
    DocumentCapability.SIGN: "SIGNATURE",
}


class DocumentIntegrationResolver:
    """
    Sélectionne une intégration documentaire compatible.

    Deux niveaux de résolution sont disponibles :

    - resolve():
      résolution technique dans le registre ;

    - resolve_for_company():
      résolution métier tenant compte des intégrations
      configurées pour l'environnement client.
    """

    def __init__(
        self,
        integration_registry: (
            DocumentIntegrationRegistry | None
        ) = None,
    ) -> None:
        self.registry = (
            integration_registry
            or registry
        )

    def resolve(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
        provider_code: str | None = None,
    ) -> DocumentIntegration:
        """
        Retourne une intégration compatible enregistrée
        dans le registre.

        Si provider_code est fourni, seul ce fournisseur
        est considéré.
        """

        if provider_code:
            integration = self.registry.get(
                provider_code
            )

            if not integration.provides(
                capability
            ):
                raise LookupError(
                    "Le fournisseur "
                    f"{integration.provider_code} "
                    "ne fournit pas la capacité "
                    f"{capability}."
                )

            if not integration.supports(
                version=version,
                capability=capability,
            ):
                raise LookupError(
                    "Le fournisseur "
                    f"{integration.provider_code} "
                    "ne prend pas en charge ce document."
                )

            return integration

        for integration in self.registry.all():

            if not integration.provides(
                capability
            ):
                continue

            if integration.supports(
                version=version,
                capability=capability,
            ):
                return integration

        raise LookupError(
            "Aucune intégration documentaire compatible "
            f"avec la capacité {capability}."
        )

    def resolve_for_company(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
        company,
    ) -> DocumentIntegration:
        """
        Résout l'intégration documentaire configurée
        pour une société.

        Les intégrations actives et connectées sont
        examinées par ordre de priorité.
        """

        service_type_code = (
            CAPABILITY_SERVICE_TYPE.get(
                capability
            )
        )

        if service_type_code is None:
            raise LookupError(
                "La capacité documentaire "
                f"{capability} n'est associée à aucun "
                "type de service externe."
            )

        try:
            client_environment = (
                company.client_environment
            )
        except company.__class__.client_environment.RelatedObjectDoesNotExist:
            raise LookupError(
                "La société ne possède pas "
                "d'environnement client."
            ) from None

        integrations = (
            ExternalIntegration.objects
            .filter(
                client_environment=client_environment,
                service_type__code=service_type_code,
                service_type__catalog_type__code=(
                    "INTEGRATION_SERVICE_TYPE"
                ),
                connection_status__code="CONNECTED",
                connection_status__catalog_type__code=(
                    "INTEGRATION_CONNECTION_STATUS"
                ),
                is_active=True,
            )
            .select_related(
                "provider",
                "provider__catalog_type",
            )
            .order_by(
                "priority",
                "name",
            )
        )

        for external_integration in integrations:

            provider_code = (
                external_integration.provider.code
            )

            try:
                adapter = self.registry.get(
                    provider_code
                )
            except LookupError:
                # L'intégration existe en configuration,
                # mais Easy Projet ne possède pas
                # d'adaptateur pour ce fournisseur.
                continue

            if not adapter.provides(
                capability
            ):
                continue

            if not adapter.supports(
                version=version,
                capability=capability,
            ):
                continue

            return adapter

        raise LookupError(
            "Aucune intégration documentaire active, "
            "connectée et compatible n'est configurée "
            f"pour la société {company}."
        )