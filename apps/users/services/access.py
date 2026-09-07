

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.companies.models import Company
from apps.users.models import User


class UserAccessService:
    """
    Centralise les règles d'accès aux utilisateurs.

    Trois notions sont distinguées :

    - visibilité :
      utilisateurs que l'acteur peut connaître
      dans son périmètre ;

    - administration du compte :
      modification des données globales du compte ;

    - participation projet :
      gérée séparément par les mécanismes projet.

    Règles de visibilité :
    - administrateur système :
      tous les utilisateurs ;
    - administrateur client :
      utilisateurs connus des environnements clients
      qu'il administre ;
    - utilisateur ayant accès à des projets :
      utilisateurs connus des environnements clients
      de ces projets ;
    - utilisateur inactif :
      aucun utilisateur.

    Règles d'administration :
    - administrateur système :
      tous les comptes ;
    - administrateur client :
      comptes connus des environnements clients
      qu'il administre ;
    - autres utilisateurs :
      aucune administration globale de compte.

    La société de l'utilisateur représente son employeur.
    Elle ne constitue pas un périmètre d'autorisation.
    """

    @classmethod
    def get_accessible_users(
        cls,
        user: User,
    ) -> QuerySet[User]:
        """
        Retourne les utilisateurs visibles
        par l'utilisateur courant.
        """

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
        """
        Retourne les comptes dont les données globales
        peuvent être administrées par l'utilisateur.
        """

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
        """
        Retourne les sociétés pouvant être utilisées
        comme employeur lors de l'administration
        d'un compte.

        Company constitue un annuaire global.
        Un administrateur autorisé à créer un compte
        peut donc sélectionner toute société active.
        """

        if not cls.can_create_user(user):
            return Company.objects.none()

        return (
            Company.objects
            .filter(is_active=True)
            .order_by("name")
        )

    @classmethod
    def can_create_user(
        cls,
        user: User,
    ) -> bool:
        """
        Indique si l'utilisateur peut créer
        un compte global.
        """

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
        """
        Indique si l'utilisateur peut modifier
        les données globales du compte cible.
        """

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
        """
        QuerySet de base des utilisateurs.

        Seules les relations appartenant réellement
        au modèle User sont chargées ici.
        """

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
        """
        Retourne les identifiants des environnements
        clients administrés par l'utilisateur.
        """

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
        Retourne les environnements dans lesquels
        l'utilisateur peut connaître des contacts.

        Le périmètre est constitué :
        - des environnements qu'il administre ;
        - des environnements de ses participations
          actives à des projets actifs.
        """

        administered_environment_ids = (
            cls._get_administered_environment_ids(user)
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
            administered_environment_ids
            .union(project_environment_ids)
        )