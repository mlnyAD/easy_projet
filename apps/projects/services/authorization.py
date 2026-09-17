

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.projects.models import Project, ProjectMembership
from apps.projects.services.access import ProjectAccessService
from apps.projects.services.project_manager import ProjectManagerService
from apps.users.models import User
from apps.companies.models import Company
from apps.core.models import ClientEnvironment


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

    PROJECT_ROLE_CATALOG = "USER_PROJECT_ROLE"
    PROJECT_MANAGER_ROLE = "PROJECT_MANAGER"

    ACCESS_LEVEL_CATALOG = "USER_LEVEL_ACCESS"
    STANDARD_ACCESS_LEVEL = "STANDARD"

    @classmethod
    def get_administrable_projects(
        cls,
        user: User,
    ) -> QuerySet[Project]:
        """
        Retourne les projets actifs que l'utilisateur peut administrer.

        Un projet est administrable lorsque l'utilisateur est :
        - administrateur système ;
        - administrateur client actif de l'environnement du projet ;
        - chef de projet actif du projet.

        La visibilité transverse d'un Chef de projet ne donne
        aucun droit d'administration.

        Les niveaux STANDARD et READ_ONLY ne donnent aucun droit
        d'administration du projet.
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
                    client_environment__is_active=True,
                )
                | Q(
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
            )
            .distinct()
            .order_by(
                "reference",
                "name",
            )
        )
        
    @classmethod
    def get_workable_projects(
        cls,
        user: User,
    ) -> QuerySet[Project]:
        """
        Retourne les projets actifs sur lesquels l'utilisateur peut
        effectuer du travail opérationnel.

        Sont autorisés :
        - l'administrateur système ;
        - l'administrateur client de l'environnement ;
        - le chef de projet affecté au projet ;
        - le membre actif disposant du niveau STANDARD.

        La visibilité transverse et le niveau READ_ONLY n'accordent
        aucun droit de travail.
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
                    client_environment__is_active=True,
                )
                | Q(
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
                | Q(
                    memberships__user=user,
                    memberships__is_active=True,
                    memberships__access_level__catalog_type__code=(
                        cls.ACCESS_LEVEL_CATALOG
                    ),
                    memberships__access_level__catalog_type__is_active=True,
                    memberships__access_level__code=(
                        cls.STANDARD_ACCESS_LEVEL
                    ),
                    memberships__access_level__is_active=True,
                )
            )
            .distinct()
            .order_by(
                "reference",
                "name",
            )
        )   

    @classmethod
    def get_financially_accessible_projects(
        cls,
        user: User,
    ) -> QuerySet[Project]:
        """
        Retourne les projets actifs dont l'utilisateur peut consulter
        et gérer les données financières.

        Sont autorisés :
        - l'administrateur système ;
        - l'administrateur client de l'environnement ;
        - le chef de projet affecté au projet, titulaire ou délégué.

        La visibilité transverse, les niveaux STANDARD et READ_ONLY
        n'accordent aucun accès financier.
        """

        return cls.get_administrable_projects(user)
    
    @classmethod
    def get_project_creation_companies(
        cls,
        user: User,
    ) -> QuerySet[Company]:
        """
        Retourne les sociétés pour lesquelles l'utilisateur peut
        créer un projet.

        Le périmètre comprend :
        - pour un administrateur système :
          toutes les sociétés actives disposant d'un environnement
          client actif ;
        - pour un administrateur client :
          les sociétés des environnements clients actifs qu'il
          administre ;
        - pour un chef de projet :
          les sociétés des projets actifs qu'il dirige.

        Les différents périmètres sont cumulés.

        La société employeur de l'utilisateur n'accorde aucun droit
        de création.
        """

        if not user.is_active:
            return Company.objects.none()

        active_environment_company_ids = (
            ClientEnvironment.objects
            .filter(
                is_active=True,
                company__is_active=True,
            )
            .values("company_id")
        )

        queryset = Company.objects.filter(
            is_active=True,
            pk__in=active_environment_company_ids,
        )

        if user.is_system_admin:
            return queryset.order_by("name")

        client_admin_company_ids = (
            user.client_environment_memberships
            .filter(
                client_environment__is_active=True,
                client_environment__company__is_active=True,
                is_client_admin=True,
                is_active=True,
            )
            .values("client_environment__company_id")
        )

        managed_project_company_ids = (
            ProjectMembership.objects
            .filter(
                user=user,
                is_active=True,
                project__is_active=True,
                project__company__is_active=True,
                role__catalog_type__code=cls.PROJECT_ROLE_CATALOG,
                role__catalog_type__is_active=True,
                role__code=cls.PROJECT_MANAGER_ROLE,
                role__is_active=True,
            )
            .values("project__company_id")
        )

        return (
            queryset
            .filter(
                Q(pk__in=client_admin_company_ids)
                | Q(pk__in=managed_project_company_ids)
            )
            .distinct()
            .order_by("name")
        )

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

        return (
            cls.get_administrable_projects(user)
            .filter(pk=project.pk)
            .exists()
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