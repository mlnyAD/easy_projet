

from __future__ import annotations

from django.conf import settings

from framework.bootstrap import Bootstrap, registry

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
from apps.users.models import User


class UserBootstrap(Bootstrap):
    """
    Création des utilisateurs de référence
    de l'environnement de développement.

    Les utilisateurs existants ne sont jamais supprimés.
    """

    name = "users"
    version = "1.0"
    dependencies = (
        "catalogs",
    )

    DEFAULT_PASSWORD = "EasyProjet2026!"

    USERS = (
        {
            "last_name": "BRUNE",
            "first_name": "Alice",
            "email": "alice.brune@example.test",
            "global_role": "USER",
            "access_level": "STANDARD",
            "employment_type": "EMPLOYEE",
        },
        {
            "last_name": "MARTIN",
            "first_name": "Paul",
            "email": "paul.martin@example.test",
            "global_role": "USER",
            "access_level": "STANDARD",
            "employment_type": "EMPLOYEE",
        },
        {
            "last_name": "DUPONT",
            "first_name": "Claire",
            "email": "claire.dupont@example.test",
            "global_role": "USER",
            "access_level": "STANDARD",
            "employment_type": "EMPLOYEE",
        },
        {
            "last_name": "DURAND",
            "first_name": "Marc",
            "email": "marc.durand@example.test",
            "global_role": "USER",
            "access_level": "STANDARD",
            "employment_type": "EMPLOYEE",
        },
        {
            "last_name": "ADMIN",
            "first_name": "Client",
            "email": "admin.client@example.test",
            "global_role": "CLIENT_ADMIN",
            "access_level": "ADMIN",
            "employment_type": "EMPLOYEE",
        },
        {
            "last_name": "ADMIN",
            "first_name": "Système",
            "email": "admin.system@example.test",
            "global_role": "SYSTEM_ADMIN",
            "access_level": "ADMIN",
            "employment_type": "EMPLOYEE",
        },
    )

    def run(self) -> None:
        if not settings.DEBUG:
            print(
                "Bootstrap users ignoré : "
                "DEBUG=False."
            )
            return

        company = self._get_company()

        for definition in self.USERS:
            self._upsert_user(
                company=company,
                definition=definition,
            )

    def _get_company(self) -> Company:
        """
        Retourne la société utilisée pour les données
        de développement.

        Pour l'instant, une seule société active doit
        exister.
        """

        companies = Company.objects.filter(
            is_active=True
        )

        count = companies.count()

        if count == 0:
            raise RuntimeError(
                "Aucune société active n'existe."
            )

        if count > 1:
            raise RuntimeError(
                "Plusieurs sociétés actives existent. "
                "Le bootstrap users ne peut pas choisir "
                "automatiquement la société."
            )

        return companies.get()

    def _catalog_value(
        self,
        *,
        catalog_code: str,
        value_code: str,
    ) -> CatalogValue:
        return CatalogValue.objects.get(
            catalog_type__code=catalog_code,
            catalog_type__is_active=True,
            code=value_code,
            is_active=True,
        )

    def _upsert_user(
        self,
        *,
        company: Company,
        definition: dict,
    ) -> None:
        email = definition["email"]

        global_role = self._catalog_value(
            catalog_code="USER_GLOBAL_ROLE",
            value_code=definition["global_role"],
        )

        access_level = self._catalog_value(
            catalog_code="USER_LEVEL_ACCESS",
            value_code=definition["access_level"],
        )

        employment_type = self._catalog_value(
            catalog_code="USER_EMPLOYMENT_TYPE",
            value_code=definition[
                "employment_type"
            ],
        )

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "last_name": definition["last_name"],
                "first_name": definition["first_name"],
                "company": company,
                "global_role": global_role,
                "access_level": access_level,
                "employment_type": employment_type,
                "is_active": True,
            },
        )

        if created:
            user.set_password(
                self.DEFAULT_PASSWORD
            )
            user.save()

            print(
                f"Utilisateur créé : {user.email}"
            )
            return

        user.last_name = definition["last_name"]
        user.first_name = definition["first_name"]
        user.company = company
        user.global_role = global_role
        user.access_level = access_level
        user.employment_type = employment_type
        user.is_active = True

        user.save()

        print(
            f"Utilisateur existant : {user.email}"
        )


registry.register(UserBootstrap())