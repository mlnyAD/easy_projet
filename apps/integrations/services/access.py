

from __future__ import annotations

from django.db.models import QuerySet

from apps.core.models import ClientEnvironment
from apps.integrations.models import ExternalIntegration
from apps.users.models import User


class IntegrationAccessService:
    """
    Centralise les règles d'accès aux intégrations externes.

    Règles :
    - SYSTEM_ADMIN :
      accès à toutes les intégrations ;
      accès à tous les environnements clients actifs ;
      création et modification autorisées.
    - CLIENT_ADMIN :
      accès aux intégrations de son ClientEnvironment ;
      seul son ClientEnvironment est assignable ;
      création et modification autorisées dans ce périmètre.
    - autres utilisateurs :
      aucun accès aux intégrations ;
      aucun environnement assignable ;
      création et modification interdites.
    """

    GLOBAL_ROLE_CATALOG = "USER_GLOBAL_ROLE"

    ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
    ROLE_CLIENT_ADMIN = "CLIENT_ADMIN"

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

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return cls._base_queryset()

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            environment = cls._get_user_client_environment(user)

            if environment is None:
                return ExternalIntegration.objects.none()

            return cls._base_queryset().filter(
                client_environment=environment,
            )

        return ExternalIntegration.objects.none()

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

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return (
                ClientEnvironment.objects
                .filter(is_active=True)
                .select_related("company")
                .order_by("company__name")
            )

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            environment = cls._get_user_client_environment(user)

            if environment is None or not environment.is_active:
                return ClientEnvironment.objects.none()

            return (
                ClientEnvironment.objects
                .filter(pk=environment.pk)
                .select_related("company")
                .order_by("company__name")
            )

        return ClientEnvironment.objects.none()

    @classmethod
    def can_view_integration(
        cls,
        user: User,
        integration: ExternalIntegration,
    ) -> bool:
        """
        Indique si l'utilisateur peut consulter une intégration.
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
        Indique si l'utilisateur peut créer une intégration.
        """

        if not user.is_active:
            return False

        return cls._get_global_role_code(user) in {
            cls.ROLE_SYSTEM_ADMIN,
            cls.ROLE_CLIENT_ADMIN,
        }

    @classmethod
    def can_update_integration(
        cls,
        user: User,
        integration: ExternalIntegration,
    ) -> bool:
        """
        Indique si l'utilisateur peut modifier une intégration.

        La modification nécessite :
        - un rôle autorisé ;
        - l'appartenance de l'intégration au périmètre visible.
        """

        if not user.is_active:
            return False

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return True

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            return cls.can_view_integration(
                user,
                integration,
            )

        return False

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
    def _get_global_role_code(
        cls,
        user: User,
    ) -> str | None:
        """
        Retourne le code du rôle global si celui-ci
        appartient au catalogue USER_GLOBAL_ROLE.
        """

        role = user.global_role

        if role is None:
            return None

        if role.catalog_type.code != cls.GLOBAL_ROLE_CATALOG:
            return None

        return role.code

    @staticmethod
    def _get_user_client_environment(
        user: User,
    ) -> ClientEnvironment | None:
        """
        Retourne le ClientEnvironment de la société
        de l'utilisateur.
        """

        try:
            return user.company.client_environment
        except ClientEnvironment.DoesNotExist:
            return None