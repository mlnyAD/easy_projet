

from __future__ import annotations

from django.db.models import QuerySet

from apps.core.models import ClientEnvironment
from apps.integrations.models import ExternalIntegration
from apps.users.models import User


class IntegrationAccessService:
    """
    Centralise les règles d'accès aux intégrations externes.

    Règles :
    - administrateur système :
      accès à toutes les intégrations ;
      accès à tous les environnements clients actifs ;
      création et modification autorisées ;

    - administrateur client :
      accès aux intégrations des environnements clients
      qu'il administre ;
      seuls ces environnements sont assignables ;
      création et modification autorisées dans ce périmètre ;

    - autres utilisateurs :
      aucun accès aux intégrations.
    """

    @classmethod
    def get_accessible_integrations(
        cls,
        user: User,
    ) -> QuerySet[ExternalIntegration]:
        """
        Retourne les intégrations visibles par l'utilisateur.
        """

        if not user.is_active:
            return ExternalIntegration.objects.none()

        if user.is_system_admin:
            return cls._base_queryset()

        environment_ids = (
            cls._get_administered_environment_ids(user)
        )

        return (
            cls._base_queryset()
            .filter(
                client_environment_id__in=environment_ids,
            )
            .distinct()
        )

    @classmethod
    def get_assignable_environments(
        cls,
        user: User,
    ) -> QuerySet[ClientEnvironment]:
        """
        Retourne les environnements clients qu'un utilisateur
        peut sélectionner lors de la création ou de la
        modification d'une intégration.
        """

        if not user.is_active:
            return ClientEnvironment.objects.none()

        queryset = (
            ClientEnvironment.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by("company__name")
        )

        if user.is_system_admin:
            return queryset

        environment_ids = (
            cls._get_administered_environment_ids(user)
        )

        return queryset.filter(
            pk__in=environment_ids,
        )

    @classmethod
    def can_view_integration(
        cls,
        user: User,
        integration: ExternalIntegration,
    ) -> bool:
        """
        Indique si l'utilisateur peut consulter
        une intégration.
        """

        return (
            cls.get_accessible_integrations(user)
            .filter(pk=integration.pk)
            .exists()
        )

    @classmethod
    def can_create_integration(
        cls,
        user: User,
    ) -> bool:
        """
        Indique si l'utilisateur peut créer
        une intégration.
        """

        if not user.is_active:
            return False

        if user.is_system_admin:
            return True

        return (
            cls._get_administered_environment_ids(user)
            .exists()
        )

    @classmethod
    def can_update_integration(
        cls,
        user: User,
        integration: ExternalIntegration,
    ) -> bool:
        """
        Indique si l'utilisateur peut modifier
        une intégration.
        """

        if not user.is_active:
            return False

        if user.is_system_admin:
            return True

        return cls.can_view_integration(
            user,
            integration,
        )

    @classmethod
    def _base_queryset(
        cls,
    ) -> QuerySet[ExternalIntegration]:
        """
        QuerySet commun des intégrations externes.
        """

        return (
            ExternalIntegration.objects
            .select_related(
                "client_environment",
                "client_environment__company",
                "service_type",
                "provider",
                "connection_status",
            )
            .order_by(
                "client_environment__company__name",
                "service_type__sort_order",
                "priority",
                "name",
            )
        )

    @classmethod
    def _get_administered_environment_ids(
        cls,
        user: User,
    ) -> QuerySet:
        """
        Retourne les environnements clients actifs
        administrés par l'utilisateur.
        """

        return (
            user.client_environment_memberships
            .filter(
                is_active=True,
                is_client_admin=True,
                client_environment__is_active=True,
            )
            .values_list(
                "client_environment_id",
                flat=True,
            )
        )