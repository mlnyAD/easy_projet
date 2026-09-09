

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
      accès à tous les projets actifs ;
    - administrateur client :
      accès à tous les projets actifs des environnements
      clients qu'il administre ;
    - membre d'un projet :
      accès direct aux projets pour lesquels un
      ProjectMembership actif existe ;
    - Chef de projet :
      accès en consultation aux autres projets actifs
      des sociétés des projets qu'il dirige.

    Un utilisateur peut cumuler plusieurs périmètres.

    La visibilité transverse d'un Chef de projet est déterminée
    par la société des projets qu'il dirige et non par sa société
    employeur.

    Ce service détermine uniquement si un projet est visible.
    Il ne détermine pas les actions autorisées sur ce projet.
    """

    PROJECT_MANAGER_ROLE_CODE = "PROJECT_MANAGER"

    @classmethod
    def get_accessible_projects(
        cls,
        user: User,
    ) -> QuerySet[Project]:
        """
        Retourne les projets actifs visibles par l'utilisateur.
        """

        if not user.is_active:
            return Project.objects.none()

        queryset = (
            Project.objects
            .filter(is_active=True)
            .select_related(
                "client_environment",
                "client_environment__company",
                "company",
                "status",
            )
        )

        if user.is_system_admin:
            return queryset.order_by(
                "reference",
                "name",
            )

        managed_company_ids = (
            user.project_memberships
            .filter(
                is_active=True,
                project__is_active=True,
                role__catalog_type__code="USER_PROJECT_ROLE",
                role__code=cls.PROJECT_MANAGER_ROLE_CODE,
            )
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
    ) -> bool:
        """
        Indique si l'utilisateur peut voir le projet.

        Un résultat True ne signifie pas nécessairement que
        l'utilisateur peut modifier ou administrer le projet.
        """

        return (
            cls.get_accessible_projects(user)
            .filter(pk=project.pk)
            .exists()
        )