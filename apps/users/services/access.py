

from __future__ import annotations

from django.db.models import QuerySet

from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.users.models import User


class UserAccessService:
    """
    Centralise les règles d'accès aux utilisateurs.
    """

    @classmethod
    def get_accessible_users(
        cls,
        user: User,
    ) -> QuerySet[User]:
        if not user.is_active:
            return User.objects.none()

        if user.is_system_admin:
            return cls._base_queryset()

        environment_ids = (
            cls._get_visible_environment_ids(user)
        )

        if not environment_ids:
            return User.objects.none()

        return (
            cls._base_queryset()
            .filter(
                client_environment_memberships__client_environment_id__in=(
                    environment_ids
                ),
                client_environment_memberships__is_active=True,
            )
            .distinct()
        )

    @classmethod
    def get_administrable_users(
        cls,
        user: User,
    ) -> QuerySet[User]:
        if not user.is_active:
            return User.objects.none()

        if user.is_system_admin:
            return cls._base_queryset()

        environment_ids = (
            cls._get_administered_environment_ids(user)
        )

        if not environment_ids:
            return User.objects.none()

        return (
            cls._base_queryset()
            .filter(
                client_environment_memberships__client_environment_id__in=(
                    environment_ids
                ),
                client_environment_memberships__is_active=True,
            )
            .distinct()
        )

    @classmethod
    def get_assignable_companies(
        cls,
        user: User,
    ) -> QuerySet[Company]:
        if not cls.can_create_user(user):
            return Company.objects.none()

        return (
            Company.objects
            .filter(is_active=True)
            .order_by("name")
        )

    @classmethod
    def get_assignable_client_environments(
        cls,
        user: User,
    ) -> QuerySet[ClientEnvironment]:
        """
        Retourne les environnements auxquels l'acteur
        peut rattacher un utilisateur.
        """

        if not user.is_active:
            return ClientEnvironment.objects.none()

        if user.is_system_admin:
            return (
                ClientEnvironment.objects
                .filter(
                    is_active=True,
                )
                .select_related(
                    "company",
                )
                .order_by(
                    "company__name",
                )
            )

        return (
            ClientEnvironment.objects
            .filter(
                pk__in=(
                    cls._get_administered_environment_ids(
                        user
                    )
                ),
                is_active=True,
            )
            .select_related(
                "company",
            )
            .order_by(
                "company__name",
            )
        )

    @classmethod
    def get_administrable_client_environment_memberships(
        cls,
        user: User,
        target_user: User,
    ) -> QuerySet[ClientEnvironmentMembership]:
        """
        Retourne les rattachements client du compte cible
        pouvant être administrés par l'acteur.
        """

        queryset = (
            ClientEnvironmentMembership.objects
            .filter(
                user=target_user,
            )
            .select_related(
                "client_environment",
                "client_environment__company",
                "employment_type",
                "user",
            )
            .order_by(
                "client_environment__company__name",
            )
        )

        if not user.is_active:
            return queryset.none()

        if user.is_system_admin:
            return queryset

        return queryset.filter(
            client_environment_id__in=(
                cls._get_administered_environment_ids(
                    user
                )
            )
        )

    @classmethod
    def can_create_client_environment_membership(
        cls,
        user: User,
        target_user: User,
    ) -> bool:
        """
        Indique si l'acteur peut créer un rattachement
        client pour l'utilisateur cible.
        """

        if not user.is_active:
            return False

        if user.is_system_admin:
            return True

        return cls.can_update_user(
            user,
            target_user,
        )

    @classmethod
    def can_update_client_environment_membership(
        cls,
        user: User,
        membership: ClientEnvironmentMembership,
    ) -> bool:
        """
        Indique si l'acteur peut modifier un rattachement
        client existant.
        """

        if not user.is_active:
            return False

        if user.is_system_admin:
            return True

        return (
            cls.get_administrable_client_environment_memberships(
                user,
                membership.user,
            )
            .filter(
                pk=membership.pk,
            )
            .exists()
        )

    @classmethod
    def can_create_user(
        cls,
        user: User,
    ) -> bool:
        if not user.is_active:
            return False

        if user.is_system_admin:
            return True

        return (
            cls._get_administered_environment_ids(user)
            .exists()
        )

    @classmethod
    def can_update_user(
        cls,
        user: User,
        target_user: User,
    ) -> bool:
        if not user.is_active:
            return False

        if user.is_system_admin:
            return True

        return (
            cls.get_administrable_users(user)
            .filter(pk=target_user.pk)
            .exists()
        )

    @classmethod
    def can_reset_temporary_password(
        cls,
        user: User,
        target_user: User,
    ) -> bool:
        return cls.can_update_user(
            user,
            target_user,
        )

    @classmethod
    def _base_queryset(
        cls,
    ) -> QuerySet[User]:
        return (
            User.objects
            .select_related(
                "company",
                "job",
            )
            .order_by(
                "last_name",
                "first_name",
            )
        )

    @classmethod
    def _get_administered_environment_ids(
        cls,
        user: User,
    ) -> QuerySet:
        return (
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

    @classmethod
    def _get_visible_environment_ids(
        cls,
        user: User,
    ):
        """
        Retourne les environnements dans lesquels l'utilisateur
        peut consulter les contacts.

        Le périmètre est constitué :
        - des environnements auxquels il est directement rattaché ;
        - des environnements qu'il administre ;
        - des environnements de ses participations actives
          à des projets actifs.
        """

        membership_environment_ids = (
            user.client_environment_memberships
            .filter(
                is_active=True,
                client_environment__is_active=True,
            )
            .values_list(
                "client_environment_id",
                flat=True,
            )
        )

        administered_environment_ids = (
            cls._get_administered_environment_ids(
                user
            )
        )

        project_environment_ids = (
            user.project_memberships
            .filter(
                is_active=True,
                project__is_active=True,
                project__client_environment__is_active=True,
            )
            .values_list(
                "project__client_environment_id",
                flat=True,
            )
        )

        return (
            membership_environment_ids
            .union(
                administered_environment_ids,
            )
            .union(
                project_environment_ids,
            )
        )