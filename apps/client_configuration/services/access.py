

from __future__ import annotations

from django.db.models import Q

from apps.core.models import ClientEnvironment
from apps.projects.models import Project


class ClientConfigurationAccessService:
    """
    Gère les droits d'accès à la configuration client
    et aux commandes de maintenance.
    """

    PROJECT_ROLE_CATALOG = "USER_PROJECT_ROLE"
    PROJECT_MANAGER_ROLE = "PROJECT_MANAGER"

    @classmethod
    def get_manageable_client_environments(
        cls,
        user,
    ):
        queryset = (
            ClientEnvironment.objects
            .filter(
                is_active=True,
                company__is_active=True,
            )
            .select_related(
                "company",
            )
            .order_by(
                "company__name",
            )
        )

        if (
            not user.is_authenticated
            or not user.is_active
        ):
            return queryset.none()

        if user.is_system_admin:
            return queryset

        return queryset.filter(
            Q(
                user_memberships__user=user,
                user_memberships__is_active=True,
                user_memberships__is_client_admin=True,
            )
            |
            Q(
                projects__memberships__user=user,
                projects__memberships__is_active=True,
                projects__is_active=True,
                projects__memberships__role__catalog_type__code=(
                    cls.PROJECT_ROLE_CATALOG
                ),
                projects__memberships__role__catalog_type__is_active=True,
                projects__memberships__role__code=(
                    cls.PROJECT_MANAGER_ROLE
                ),
                projects__memberships__role__is_active=True,
            )
        ).distinct()

    @classmethod
    def can_manage_client_environment(
        cls,
        user,
        client_environment: ClientEnvironment,
    ) -> bool:
        if not isinstance(
            client_environment,
            ClientEnvironment,
        ):
            return False

        return (
            cls.get_manageable_client_environments(
                user,
            )
            .filter(
                pk=client_environment.pk,
            )
            .exists()
        )

    @classmethod
    def get_maintainable_projects(
        cls,
        user,
        *,
        client_environment: ClientEnvironment,
    ):
        """
        Retourne les projets sur lesquels l'utilisateur peut
        exécuter une commande de maintenance.

        Les administrateurs système et client disposent de
        l'ensemble des projets de l'environnement.

        Un chef de projet, titulaire ou délégué, ne dispose
        que des projets auxquels il est activement affecté
        avec le rôle PROJECT_MANAGER.
        """

        queryset = (
            Project.objects
            .filter(
                client_environment=client_environment,
            )
            .select_related(
                "client_environment",
                "company",
            )
            .order_by(
                "reference",
                "name",
            )
        )

        if (
            not user.is_authenticated
            or not user.is_active
        ):
            return queryset.none()

        if user.is_system_admin:
            return queryset

        is_client_admin = (
            client_environment.user_memberships
            .filter(
                user=user,
                is_active=True,
                is_client_admin=True,
            )
            .exists()
        )

        if is_client_admin:
            return queryset

        return (
            queryset
            .filter(
                is_active=True,
                memberships__user=user,
                memberships__is_active=True,
                memberships__role__catalog_type__code=(
                    cls.PROJECT_ROLE_CATALOG
                ),
                memberships__role__catalog_type__is_active=True,
                memberships__role__code=(
                    cls.PROJECT_MANAGER_ROLE
                ),
                memberships__role__is_active=True,
            )
            .distinct()
        )