

from __future__ import annotations

from dataclasses import dataclass

from django.core.exceptions import ObjectDoesNotExist

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


@dataclass(frozen=True, slots=True)
class ResolvedDocumentIntegration:
    """
    Résultat d'une résolution tenant compte de la configuration client.

    L'adaptateur fournit le comportement technique ; l'intégration
    externe porte la configuration, la priorité et la référence vers
    les secrets du client.
    """

    adapter: DocumentIntegration
    external_integration: ExternalIntegration


class DocumentIntegrationResolver:
    """
    Sélectionne une intégration documentaire compatible.

    Deux niveaux de résolution sont disponibles :

    - resolve() : résolution technique dans le registre ;
    - resolve_for_company() : retourne l'adaptateur configuré ;
    - resolve_configured_for_company() : retourne à la fois
      l'adaptateur et l'ExternalIntegration sélectionnée.

    Le dernier niveau est requis notamment pour la signature, car une
    demande doit conserver le fournisseur effectivement utilisé.
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
        Retourne une intégration compatible enregistrée.

        Si provider_code est fourni, seul ce fournisseur est considéré.
        """

        if provider_code:
            adapter = self.registry.get(provider_code)

            if not adapter.provides(capability):
                raise LookupError(
                    "Le fournisseur "
                    f"{adapter.provider_code} "
                    "ne fournit pas la capacité "
                    f"{capability}."
                )

            if not adapter.supports(
                version=version,
                capability=capability,
            ):
                raise LookupError(
                    "Le fournisseur "
                    f"{adapter.provider_code} "
                    "ne prend pas en charge ce document."
                )

            return adapter

        for adapter in self.registry.all():
            if not adapter.provides(capability):
                continue

            if adapter.supports(
                version=version,
                capability=capability,
            ):
                return adapter

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
        Retourne l'adaptateur configuré pour une société.

        Cette méthode conserve le contrat historique utilisé par les
        vues OnlyOffice et CADViewer.
        """

        resolved = self.resolve_configured_for_company(
            version=version,
            capability=capability,
            company=company,
        )

        return resolved.adapter

    def resolve_configured_for_company(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
        company,
    ) -> ResolvedDocumentIntegration:
        """
        Retourne l'adaptateur et sa configuration client effective.

        Les intégrations actives et connectées sont examinées dans
        l'ordre de priorité défini pour l'environnement client.
        """

        service_type_code = CAPABILITY_SERVICE_TYPE.get(
            capability
        )

        if service_type_code is None:
            raise LookupError(
                "La capacité documentaire "
                f"{capability} n'est associée à aucun "
                "type de service externe."
            )

        try:
            client_environment = company.client_environment
        except ObjectDoesNotExist:
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
            provider_code = external_integration.provider.code

            try:
                adapter = self.registry.get(provider_code)
            except LookupError:
                # Une configuration peut exister avant l'installation
                # de son adaptateur dans Easy Projet.
                continue

            if not adapter.provides(capability):
                continue

            if not adapter.supports(
                version=version,
                capability=capability,
            ):
                continue

            return ResolvedDocumentIntegration(
                adapter=adapter,
                external_integration=external_integration,
            )

        raise LookupError(
            "Aucune intégration documentaire active, "
            "connectée et compatible n'est configurée "
            f"pour la société {company}."
        )