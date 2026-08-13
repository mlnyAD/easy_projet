

from __future__ import annotations

from django.db.models import QuerySet

from apps.users.models import User
from apps.core.models import ClientEnvironment
from ..models import Project


class ProjectAccessService:
    """
    Centralise les règles d'accès aux projets.

    Règles actuelles :
    - SYSTEM_ADMIN :
      accès à tous les projets actifs.
    - CLIENT_ADMIN :
      accès à tous les projets actifs de son ClientEnvironment.
    - autres utilisateurs :
      accès uniquement aux projets pour lesquels
      un ProjectMembership actif existe.
    """

    GLOBAL_ROLE_CATALOG = "USER_GLOBAL_ROLE"

    ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
    ROLE_CLIENT_ADMIN = "CLIENT_ADMIN"

    @classmethod
    def get_accessible_projects(
        cls,
        user: User,
    ) -> QuerySet[Project]:
        """
        Retourne les projets actifs accessibles par l'utilisateur.
        """

        if not user.is_active:
            return Project.objects.none()

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return (
                Project.objects
                .filter(is_active=True)
                .select_related(
                    "client_environment",
                    "client_environment__company",
                    "company",
                    "project_manager",
                    "status",
                )
                .order_by(
                    "reference",
                    "name",
                )
            )

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            environment = cls._get_user_client_environment(user)

            if environment is None:
                return Project.objects.none()

            return (
                Project.objects
                .filter(
                    client_environment=environment,
                    is_active=True,
                )
                .select_related(
                    "client_environment",
                    "client_environment__company",
                    "company",
                    "project_manager",
                    "status",
                )
                .order_by(
                    "reference",
                    "name",
                )
            )

        return (
            Project.objects
            .filter(
                memberships__user=user,
                memberships__is_active=True,
                is_active=True,
            )
            .select_related(
                "client_environment",
                "client_environment__company",
                "company",
                "project_manager",
                "status",
            )
            .distinct()
            .order_by(
                "reference",
                "name",
            )
        )

    @classmethod
    def can_access_project(
        cls,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur peut accéder au projet.
        """
        return cls.get_accessible_projects(
            user
        ).filter(
            pk=project.pk
        ).exists()

    @classmethod
    def _get_global_role_code(
        cls,
        user: User,
    ) -> str | None:
        """
        Retourne le code du rôle global si celui-ci
        appartient bien au catalogue USER_GLOBAL_ROLE.
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
        try:
            return user.company.client_environment
        except ClientEnvironment.DoesNotExist:
            return None