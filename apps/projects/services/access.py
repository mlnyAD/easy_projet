

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.projects.models import Project
from apps.users.models import User


class ProjectAccessService:
    """
    Centralise les règles de visibilité des projets.

    Règles :
    - utilisateur inactif :
      aucun accès ;
    - administrateur système :
      accès à tous les projets de son périmètre ;
    - administrateur client :
      accès aux projets des environnements clients qu'il administre ;
    - membre d'un projet :
      accès direct aux projets pour lesquels un ProjectMembership actif
      existe ;
    - Chef de projet :
      accès en consultation aux projets des sociétés des projets
      qu'il dirige.

    ``include_inactive=False`` conserve le comportement historique :
    seuls les projets actifs sont retournés.

    ``include_inactive=True`` permet de retrouver les projets inactifs
    dans un écran explicitement prévu pour la consultation.
    """

    PROJECT_MANAGER_ROLE_CODE = "PROJECT_MANAGER"

    @classmethod
    def get_accessible_projects(
        cls,
        user: User,
        *,
        include_inactive: bool = False,
    ) -> QuerySet[Project]:
        """
        Retourne les projets visibles par l'utilisateur.

        Par défaut, seuls les projets actifs sont retournés.
        """

        if not user.is_active:
            return Project.objects.none()

        queryset = Project.objects.select_related(
            "client_environment",
            "client_environment__company",
            "company",
            "status",
        )

        if not include_inactive:
            queryset = queryset.filter(
                is_active=True,
            )

        if user.is_system_admin:
            return queryset.order_by(
                "reference",
                "name",
            )

        managed_project_memberships = (
            user.project_memberships
            .filter(
                is_active=True,
                role__catalog_type__code=(
                    "USER_PROJECT_ROLE"
                ),
                role__code=cls.PROJECT_MANAGER_ROLE_CODE,
            )
        )

        if not include_inactive:
            managed_project_memberships = (
                managed_project_memberships.filter(
                    project__is_active=True,
                )
            )

        managed_company_ids = (
            managed_project_memberships
            .values_list(
                "project__company_id",
                flat=True,
            )
        )

        return (
            queryset
            .filter(
                Q(
                    client_environment__user_memberships__user=user,
                    client_environment__user_memberships__is_active=True,
                    client_environment__user_memberships__is_client_admin=True,
                )
                | Q(
                    memberships__user=user,
                    memberships__is_active=True,
                )
                | Q(
                    company_id__in=managed_company_ids,
                )
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
        *,
        include_inactive: bool = False,
    ) -> bool:
        """
        Indique si l'utilisateur peut voir le projet.

        Par défaut, les projets inactifs restent exclus afin de
        préserver le comportement actuel des écrans opérationnels.
        """

        return (
            cls.get_accessible_projects(
                user,
                include_inactive=include_inactive,
            )
            .filter(
                pk=project.pk,
            )
            .exists()
        )