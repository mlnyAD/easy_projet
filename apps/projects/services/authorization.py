

from __future__ import annotations

from apps.projects.models import Project, ProjectMembership
from apps.projects.services.access import ProjectAccessService
from apps.projects.services.project_manager import ProjectManagerService
from apps.users.models import User


class ProjectAuthorizationService:
    """
    Centralise les autorisations d'action sur un projet.

    La visibilité d'un projet et les droits d'action sont
    volontairement séparés.

    Règles Niveau 2 :
    - administrateur système :
      tous les droits ;
    - administrateur client de l'environnement :
      tous les droits ;
    - chef de projet du projet, titulaire ou délégué :
      tous les droits ;
    - chef de projet bénéficiant uniquement d'une visibilité
      transverse :
      consultation uniquement ;
    - membre STANDARD :
      consultation et travail opérationnel ;
    - membre READ_ONLY :
      consultation uniquement ;
    - utilisateur sans périmètre :
      aucun droit.

    Les marqueurs de responsabilité
    is_client_admin_responsible et
    is_project_manager_responsible sont organisationnels
    et n'interviennent pas dans les autorisations.
    """

    ACCESS_LEVEL_CATALOG = "USER_LEVEL_ACCESS"
    STANDARD_ACCESS_LEVEL = "STANDARD"

    @classmethod
    def can_view_project(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur peut consulter le projet.
        """

        return ProjectAccessService.can_access_project(
            user=user,
            project=project,
        )

    @classmethod
    def can_work_on_project(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur peut effectuer des opérations
        métier sur le projet.

        Une visibilité transverse de Chef de projet ne donne
        aucun droit de modification.
        """

        if not cls.can_view_project(
            user=user,
            project=project,
        ):
            return False

        if user.is_system_admin:
            return True

        if cls._is_client_admin_for_project(
            user=user,
            project=project,
        ):
            return True

        if ProjectManagerService.is_project_manager(
            user=user,
            project=project,
        ):
            return True

        return cls._has_standard_project_membership(
            user=user,
            project=project,
        )

    @classmethod
    def can_administer_project(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur peut administrer le projet.

        L'administration comprend notamment les paramètres
        structurants, les participants et les sociétés
        participantes.
        """

        if not cls.can_view_project(
            user=user,
            project=project,
        ):
            return False

        if user.is_system_admin:
            return True

        if cls._is_client_admin_for_project(
            user=user,
            project=project,
        ):
            return True

        return ProjectManagerService.is_project_manager(
            user=user,
            project=project,
        )

    @classmethod
    def can_access_financial_data(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur peut accéder aux données
        financières du projet.

        La visibilité transverse d'un Chef de projet n'inclut
        jamais les données financières.
        """

        if not cls.can_view_project(
            user=user,
            project=project,
        ):
            return False

        if user.is_system_admin:
            return True

        if cls._is_client_admin_for_project(
            user=user,
            project=project,
        ):
            return True

        return ProjectManagerService.is_project_manager(
            user=user,
            project=project,
        )

    @classmethod
    def _is_client_admin_for_project(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur est administrateur client actif
        de l'environnement auquel appartient le projet.
        """

        if not user.is_active:
            return False

        return user.client_environment_memberships.filter(
            client_environment=project.client_environment,
            client_environment__is_active=True,
            is_client_admin=True,
            is_active=True,
        ).exists()

    @classmethod
    def _has_standard_project_membership(
        cls,
        *,
        user: User,
        project: Project,
    ) -> bool:
        """
        Indique si l'utilisateur possède un ProjectMembership
        actif avec un niveau d'accès STANDARD.

        READ_ONLY n'accorde donc aucun droit de travail.
        """

        if not user.is_active:
            return False

        return ProjectMembership.objects.filter(
            project=project,
            user=user,
            is_active=True,
            access_level__catalog_type__code=(
                cls.ACCESS_LEVEL_CATALOG
            ),
            access_level__catalog_type__is_active=True,
            access_level__code=cls.STANDARD_ACCESS_LEVEL,
            access_level__is_active=True,
        ).exists()