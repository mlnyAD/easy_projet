

from __future__ import annotations

from django.db.models import QuerySet

from apps.companies.models import Company
from apps.users.models import User


class UserAccessService:
    """
    Centralise les règles d'accès à l'administration
    des utilisateurs.

    Règles :
    - SYSTEM_ADMIN :
      accès à tous les utilisateurs ;
      toutes les sociétés sont assignables ;
      création, modification et réinitialisation
      du mot de passe provisoire autorisées.
    - CLIENT_ADMIN :
      accès aux utilisateurs de sa société ;
      seule sa société est assignable ;
      création, modification et réinitialisation
      autorisées dans ce périmètre.
    - autres utilisateurs :
      aucun accès à l'administration utilisateurs.
    """

    GLOBAL_ROLE_CATALOG = "USER_GLOBAL_ROLE"

    ROLE_SYSTEM_ADMIN = "SYSTEM_ADMIN"
    ROLE_CLIENT_ADMIN = "CLIENT_ADMIN"

    @classmethod
    def get_accessible_users(
        cls,
        user: User,
    ) -> QuerySet[User]:
        """
        Retourne les utilisateurs visibles dans
        l'administration.
        """

        if not user.is_active:
            return User.objects.none()

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return cls._base_queryset()

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            if user.company_id is None:
                return User.objects.none()

            return cls._base_queryset().filter(
                company_id=user.company_id,
            )

        return User.objects.none()

    @classmethod
    def get_assignable_companies(
        cls,
        user: User,
    ) -> QuerySet[Company]:
        """
        Retourne les sociétés qu'un utilisateur
        peut affecter à un compte administré.
        """

        if not user.is_active:
            return Company.objects.none()

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return (
                Company.objects
                .filter(is_active=True)
                .order_by("name")
            )

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            if user.company_id is None:
                return Company.objects.none()

            return (
                Company.objects
                .filter(
                    pk=user.company_id,
                    is_active=True,
                )
                .order_by("name")
            )

        return Company.objects.none()

    @classmethod
    def can_create_user(
        cls,
        user: User,
    ) -> bool:
        """
        Indique si l'utilisateur peut créer un compte.
        """

        if not user.is_active:
            return False

        return cls._get_global_role_code(user) in {
            cls.ROLE_SYSTEM_ADMIN,
            cls.ROLE_CLIENT_ADMIN,
        }

    @classmethod
    def can_update_user(
        cls,
        user: User,
        target_user: User,
    ) -> bool:
        """
        Indique si l'utilisateur peut modifier
        le compte cible.
        """

        if not user.is_active:
            return False

        global_role_code = cls._get_global_role_code(user)

        if global_role_code == cls.ROLE_SYSTEM_ADMIN:
            return True

        if global_role_code == cls.ROLE_CLIENT_ADMIN:
            return (
                user.company_id is not None
                and target_user.company_id == user.company_id
            )

        return False

    @classmethod
    def can_reset_temporary_password(
        cls,
        user: User,
        target_user: User,
    ) -> bool:
        """
        Indique si l'utilisateur peut régénérer
        le mot de passe provisoire du compte cible.
        """

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
                "global_role",
                "access_level",
                "employment_type",
                "job",
            )
            .order_by(
                "last_name",
                "first_name",
            )
        )

    @classmethod
    def _get_global_role_code(
        cls,
        user: User,
    ) -> str | None:
        role = user.global_role

        if role is None:
            return None

        if role.catalog_type.code != cls.GLOBAL_ROLE_CATALOG:
            return None

        return role.code