

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.projects.models import Project
from apps.users.models import User


class ProjectAccessService:
    """
    Centralise les règles d'accès aux projets.

    Règles :
    - utilisateur inactif :
      aucun accès ;
    - administrateur système :
      accès à tous les projets actifs ;
    - administrateur client :
      accès à tous les projets actifs des environnements
      clients qu'il administre ;
    - autres utilisateurs :
      accès aux projets pour lesquels un
      ProjectMembership actif existe.

    Un utilisateur peut cumuler plusieurs périmètres :
    administration d'un ou plusieurs environnements clients
    et participation directe à d'autres projets.
    """

    @classmethod
    def get_accessible_projects(
        cls,
        user: User,
    ) -> QuerySet[Project]:
        """
        Retourne les projets actifs accessibles
        par l'utilisateur.
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
        Indique si l'utilisateur peut accéder
        au projet.
        """

        return (
            cls.get_accessible_projects(user)
            .filter(pk=project.pk)
            .exists()
        )