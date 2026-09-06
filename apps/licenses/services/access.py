

from __future__ import annotations

from django.db.models import QuerySet

from apps.core.models import ClientEnvironment
from apps.licenses.models import License
from apps.projects.services.access import ProjectAccessService
from apps.users.models import User


class LicenseAccessService:
    """
    Centralise les règles d'accès aux licences.

    Règles :
    - SYSTEM_ADMIN :
      accès à toutes les licences ;
      création et modification autorisées.
    - CLIENT_ADMIN :
      consultation des licences de son ClientEnvironment ;
      aucune création ni modification.
    - PROJECT_MANAGER :
      consultation des licences des ClientEnvironment
      correspondant à ses projets accessibles ;
      aucune création ni modification.
    - autres utilisateurs :
      aucun accès aux licences.
    """

    GLOBAL_ROLE_CATALOG = "USER_GLOBAL_ROLE"

    ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
    ROLE_CLIENT_ADMIN = "CLIENT_ADMIN"
    ROLE_PROJECT_MANAGER = "PROJECT_MANAGER"

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

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return cls._base_queryset()

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            environment = cls._get_user_client_environment(user)

            if environment is None:
                return License.objects.none()

            return cls._base_queryset().filter(
                client_environment=environment,
            )

        if global_role_code == cls.ROLE_PROJECT_MANAGER:
            accessible_projects = (
                ProjectAccessService
                .get_accessible_projects(user)
            )

            environment_ids = (
                accessible_projects
                .values_list(
                    "client_environment_id",
                    flat=True,
                )
                .distinct()
            )

            return cls._base_queryset().filter(
                client_environment_id__in=environment_ids,
            )

        return License.objects.none()

    @classmethod
    def can_view_license(
        cls,
        user: User,
        license_instance: License,
    ) -> bool:
        """
        Indique si l'utilisateur peut consulter une licence.
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
        Indique si l'utilisateur peut créer une licence.
        """

        if not user.is_active:
            return False

        return (
            cls._get_global_role_code(user)
            == cls.ROLE_SYSTEM_ADMIN
        )

    @classmethod
    def can_update_license(
        cls,
        user: User,
        license_instance: License | None = None,
    ) -> bool:
        """
        Indique si l'utilisateur peut modifier une licence.

        La licence est acceptée en paramètre afin de conserver
        une API adaptée aux contrôles objet, même si la règle
        actuelle dépend uniquement du rôle global.
        """

        if not user.is_active:
            return False

        return (
            cls._get_global_role_code(user)
            == cls.ROLE_SYSTEM_ADMIN
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
        Retourne le ClientEnvironment de la société employeur.

        Cette relation n'est utilisée que pour CLIENT_ADMIN.

        Elle n'est volontairement pas utilisée pour PROJECT_MANAGER,
        dont le périmètre est dérivé des projets accessibles.
        """

        try:
            return user.company.client_environment
        except ClientEnvironment.DoesNotExist:
            return None