

from __future__ import annotations

from framework.bootstrap import Bootstrap, registry

from apps.companies.models import Company


class CompanyBootstrap(Bootstrap):
    """
    Création des sociétés de référence nécessaires
    au bootstrap de l'environnement de développement.
    """

    name = "companies"
    version = "1.0"
    dependencies = ()

    COMPANY_NAME = "AXCIO-DATA"
    COMPANY_EMAIL = "contact@axcio-data.com"

    def run(self) -> None:
        company, created = Company.objects.get_or_create(
            name=self.COMPANY_NAME,
            defaults={
                "email": self.COMPANY_EMAIL,
                "is_active": True,
            },
        )

        if created:
            print(
                f"Société créée : {company.name}"
            )
            return

        company.email = self.COMPANY_EMAIL
        company.is_active = True
        company.save()

        print(
            f"Société existante : {company.name}"
        )


registry.register(
    CompanyBootstrap()
)