

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from apps.documents.models import DocumentVersion

from .capabilities import DocumentCapability


class DocumentIntegration(ABC):
    """
    Contrat commun des intégrations documentaires.

    Une intégration représente un adaptateur vers un outil externe :
    OnlyOffice, CADViewer, Microsoft 365, service de signature, etc.

    Le noyau GED ne dépend jamais directement de ces fournisseurs.
    """

    provider_code: str

    capabilities: frozenset[DocumentCapability]

    def provides(
        self,
        capability: DocumentCapability,
    ) -> bool:
        """
        Indique si l'intégration fournit la capacité demandée.
        """

        return capability in self.capabilities

    @abstractmethod
    def supports(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
    ) -> bool:
        """
        Indique si l'intégration peut traiter cette version
        pour la capacité demandée.

        Le contrôle peut notamment dépendre :
        - du type MIME ;
        - de l'extension ;
        - des capacités du fournisseur.
        """

        raise NotImplementedError

    @abstractmethod
    def open(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
        user,
        return_url: str | None = None,
    ) -> Any:
        """
        Prépare l'ouverture du document avec l'intégration.

        return_url permet à une intégration de proposer
        un retour vers la page Easy Projet appelante.
        """

        raise NotImplementedError