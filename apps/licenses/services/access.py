
        
from __future__ import annotations

from django.db.models import QuerySet

from apps.licenses.models import License
from apps.projects.services.access import ProjectAccessService
from apps.users.models import User


class LicenseAccessService:
    """
    Centralise les règles d'accès aux licences.

    Règles :
    - administrateur système :
      accès à toutes les licences ;
      création et modification autorisées ;

    - administrateur client :
      consultation des licences des environnements
      clients qu'il administre ;

    - utilisateur disposant de projets accessibles :
      consultation des licences des environnements
      clients correspondant à ces projets ;

    - création et modification :
      réservées à l'administrateur système.
    """

    @classmethod
    def get_accessible_licenses(
        cls,
        user: User,
    ) -> QuerySet[License]:
        """
        Retourne les licences visibles par l'utilisateur.
        """

        if not user.is_active:
            return License.objects.none()

        if user.is_system_admin:
            return cls._base_queryset()

        administered_environment_ids = (
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

        project_environment_ids = (
            ProjectAccessService
            .get_accessible_projects(user)
            .values_list(
                "client_environment_id",
                flat=True,
            )
        )

        environment_ids = (
            administered_environment_ids
            .union(project_environment_ids)
        )

        return (
            cls._base_queryset()
            .filter(
                client_environment_id__in=environment_ids,
            )
            .distinct()
        )

    @classmethod
    def can_view_license(
        cls,
        user: User,
        license_instance: License,
    ) -> bool:
        """
        Indique si l'utilisateur peut consulter
        une licence.
        """

        return (
            cls.get_accessible_licenses(user)
            .filter(pk=license_instance.pk)
            .exists()
        )

    @classmethod
    def can_create_license(
        cls,
        user: User,
    ) -> bool:
        """
        Indique si l'utilisateur peut créer
        une licence.
        """

        return (
            user.is_active
            and user.is_system_admin
        )

    @classmethod
    def can_update_license(
        cls,
        user: User,
        license_instance: License | None = None,
    ) -> bool:
        """
        Indique si l'utilisateur peut modifier
        une licence.
        """

        return (
            user.is_active
            and user.is_system_admin
        )

    @classmethod
    def _base_queryset(
        cls,
    ) -> QuerySet[License]:
        """
        QuerySet commun des licences.
        """

        return (
            License.objects
            .select_related(
                "client_environment",
                "client_environment__company",
                "status",
            )
            .order_by(
                "-granted_at",
                "reference",
            )
        )