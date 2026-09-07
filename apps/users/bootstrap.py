

from __future__ import annotations

from django.conf import settings

from framework.bootstrap import Bootstrap, registry

from apps.companies.models import Company
from apps.users.models import User


class UserBootstrap(Bootstrap):
    """
    Création de l'administrateur système
    de l'environnement de développement.

    L'utilisateur existant n'est jamais supprimé.
    """

    name = "users"
    version = "1.0"
    dependencies = (
        "companies",
    )

    DEFAULT_PASSWORD = "EasyProjet2026!"

    SYSTEM_ADMIN = {
        "last_name": "ADMIN",
        "first_name": "Système",
    }

    def run(self) -> None:
        if not settings.DEBUG:
            print(
                "Bootstrap users ignoré : "
                "DEBUG=False."
            )
            return

        email = settings.SYSTEM_ADMIN_EMAIL

        if not email:
            raise RuntimeError(
                "EASY_PROJET_SYSTEM_ADMIN_EMAIL "
                "n'est pas configurée."
            )

        company = self._get_company()

        self._upsert_user(
            company=company,
            email=email,
            definition=self.SYSTEM_ADMIN,
        )

    def _get_company(self) -> Company:
        """
        Retourne la société utilisée pour
        l'administrateur système.

        Une seule société active doit exister
        au moment du bootstrap.
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

    def _upsert_user(
        self,
        *,
        company: Company,
        email: str,
        definition: dict,
    ) -> None:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "last_name": definition["last_name"],
                "first_name": definition["first_name"],
                "company": company,
                "is_system_admin": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(
                self.DEFAULT_PASSWORD
            )
            user.save()

            print(
                f"Administrateur système créé : "
                f"{user.email}"
            )
            return

        user.last_name = definition["last_name"]
        user.first_name = definition["first_name"]
        user.company = company
        user.is_system_admin = True
        user.is_active = True

        user.save()

        print(
            f"Administrateur système existant : "
            f"{user.email}"
        )


registry.register(
    UserBootstrap()
)