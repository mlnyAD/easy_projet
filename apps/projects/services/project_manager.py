

from __future__ import annotations

from django.db.models import QuerySet

from apps.projects.models import Project, ProjectMembership
from apps.users.models import User


class ProjectManagerService:
    """
    Centralise l'accès aux chefs de projet.

    La source de vérité est ProjectMembership.

    Un chef de projet :
    - possède un ProjectMembership actif ;
    - possède le rôle PROJECT_MANAGER.

    Parmi les chefs de projet, zéro ou un peut être
    désigné comme titulaire.

    Titulaire et délégués disposent des mêmes droits.
    """

    PROJECT_ROLE_CATALOG = "USER_PROJECT_ROLE"
    PROJECT_MANAGER_ROLE = "PROJECT_MANAGER"

    @classmethod
    def get_project_managers(
        cls,
        project: Project,
    ) -> QuerySet[ProjectMembership]:
        """
        Retourne tous les chefs de projet actifs.

        Le titulaire est retourné en premier,
        puis les autres chefs de projet par nom.
        """

        return (
            ProjectMembership.objects
            .filter(
                project=project,
                is_active=True,
                role__catalog_type__code=(
                    cls.PROJECT_ROLE_CATALOG
                ),
                role__catalog_type__is_active=True,
                role__code=cls.PROJECT_MANAGER_ROLE,
                role__is_active=True,
            )
            .select_related(
                "user",
                "user__company",
                "role",
                "access_level",
            )
            .order_by(
                "-is_project_manager_responsible",
                "user__last_name",
                "user__first_name",
            )
        )

    @classmethod
    def get_responsible_project_manager_membership(
        cls,
        project: Project,
    ) -> ProjectMembership | None:
        """
        Retourne l'affectation du chef de projet titulaire.

        Retourne None lorsqu'aucun titulaire n'est désigné.
        """

        return (
            cls.get_project_managers(project)
            .filter(
                is_project_manager_responsible=True,
            )
            .first()
        )

    @classmethod
    def get_responsible_project_manager(
        cls,
        project: Project,
    ) -> User | None:
        """
        Retourne l'utilisateur chef de projet titulaire.

        Retourne None lorsqu'aucun titulaire n'est désigné.
        """

        membership = (
            cls.get_responsible_project_manager_membership(
                project
            )
        )

        if membership is None:
            return None

        return membership.user

    @classmethod
    def is_project_manager(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur est chef de projet actif.
        """

        if not user.is_active:
            return False

        return (
            cls.get_project_managers(project)
            .filter(user=user)
            .exists()
        )

    @classmethod
    def is_responsible_project_manager(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur est le chef de projet titulaire.
        """

        if not user.is_active:
            return False

        return (
            cls.get_project_managers(project)
            .filter(
                user=user,
                is_project_manager_responsible=True,
            )
            .exists()
        )