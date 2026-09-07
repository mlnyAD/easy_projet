

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
from apps.core.models import (
    ClientEnvironment,
    ClientEnvironmentMembership,
)
from apps.projects.models import (
    Project,
    ProjectCompany,
    ProjectMembership,
)
from apps.users.models import User


class Command(BaseCommand):
    """
    Crée un jeu de données minimal pour la validation Level 2.

    Le scénario contient :
    - une société cliente ;
    - un environnement client ;
    - un chef de projet titulaire ;
    - un chef de projet délégué ;
    - un utilisateur standard ;
    - un projet ;
    - les rattachements à l'environnement client ;
    - les affectations au projet.

    La commande est réexécutable sans duplication.
    """

    help = (
        "Crée ou met à jour le jeu de données de validation Level 2."
    )

    COMPANY_NAME = "TEST LEVEL 2"

    PROJECT_REFERENCE = "L2-TEST-001"
    PROJECT_NAME = "Projet de validation Level 2"

    RESPONSIBLE_EMAIL = "cp.titulaire.level2@example.test"
    DELEGATE_EMAIL = "cp.delegue.level2@example.test"
    USER_EMAIL = "utilisateur.level2@example.test"

    def handle(self, *args, **options):
        with transaction.atomic():
            catalogs = self._get_catalog_values()

            company = self._create_company()

            client_environment = (
                self._create_client_environment(
                    company=company,
                )
            )

            responsible = self._create_user(
                email=self.RESPONSIBLE_EMAIL,
                last_name="TITULAIRE",
                first_name="Claire",
                company=company,
            )

            delegate = self._create_user(
                email=self.DELEGATE_EMAIL,
                last_name="DELEGUE",
                first_name="David",
                company=company,
            )

            standard_user = self._create_user(
                email=self.USER_EMAIL,
                last_name="UTILISATEUR",
                first_name="Emma",
                company=company,
            )

            self._create_environment_membership(
                client_environment=client_environment,
                user=responsible,
                employment_type=catalogs[
                    "employment_type"
                ],
            )

            self._create_environment_membership(
                client_environment=client_environment,
                user=delegate,
                employment_type=catalogs[
                    "employment_type"
                ],
            )

            self._create_environment_membership(
                client_environment=client_environment,
                user=standard_user,
                employment_type=catalogs[
                    "employment_type"
                ],
            )

            project = self._create_project(
                company=company,
                status=catalogs["project_status"],
            )

            self._create_project_company(
                project=project,
                company=company,
            )

            self._create_project_membership(
                project=project,
                user=responsible,
                role=catalogs["project_manager_role"],
                access_level=catalogs["access_level"],
                responsible=True,
            )

            self._create_project_membership(
                project=project,
                user=delegate,
                role=catalogs["project_manager_role"],
                access_level=catalogs["access_level"],
                responsible=False,
            )

            self._create_project_membership(
                project=project,
                user=standard_user,
                role=catalogs["user_role"],
                access_level=catalogs["access_level"],
                responsible=False,
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Jeu de données Level 2 créé avec succès."
            )
        )
        self.stdout.write("")
        self.stdout.write(
            f"Société : {company.name}"
        )
        self.stdout.write(
            f"Projet  : {project.reference} - {project.name}"
        )
        self.stdout.write("")
        self.stdout.write(
            "Chef de projet titulaire : "
            f"{responsible} <{responsible.email}>"
        )
        self.stdout.write(
            "Chef de projet délégué   : "
            f"{delegate} <{delegate.email}>"
        )
        self.stdout.write(
            "Utilisateur standard     : "
            f"{standard_user} <{standard_user.email}>"
        )

    # ------------------------------------------------------------------
    # Catalogues
    # ------------------------------------------------------------------

    def _get_catalog_values(self) -> dict[str, CatalogValue]:
        return {
            "project_status": self._get_catalog_value(
                catalog_code="PROJECT_STATUS",
                value_code="IN_PROGRESS",
            ),
            "project_manager_role": self._get_catalog_value(
                catalog_code="USER_PROJECT_ROLE",
                value_code="PROJECT_MANAGER",
            ),
            "user_role": self._get_catalog_value(
                catalog_code="USER_PROJECT_ROLE",
                value_code="USER",
            ),
            "access_level": self._get_catalog_value(
                catalog_code="USER_LEVEL_ACCESS",
                value_code="STANDARD",
            ),
            "employment_type": self._get_catalog_value(
                catalog_code="USER_EMPLOYMENT_TYPE",
                value_code="EMPLOYEE",
            ),
        }

    @staticmethod
    def _get_catalog_value(
        *,
        catalog_code: str,
        value_code: str,
    ) -> CatalogValue:
        try:
            return (
                CatalogValue.objects
                .select_related("catalog_type")
                .get(
                    catalog_type__code=catalog_code,
                    catalog_type__is_active=True,
                    code=value_code,
                    is_active=True,
                )
            )
        except CatalogValue.DoesNotExist as exc:
            raise RuntimeError(
                "Valeur de catalogue absente ou inactive : "
                f"{catalog_code}.{value_code}"
            ) from exc

    # ------------------------------------------------------------------
    # Société / environnement
    # ------------------------------------------------------------------

    def _create_company(self) -> Company:
        company, _ = Company.objects.update_or_create(
            name=self.COMPANY_NAME,
            defaults={
                "is_active": True,
            },
        )

        return company

    @staticmethod
    def _create_client_environment(
        *,
        company: Company,
    ) -> ClientEnvironment:
        client_environment, _ = (
            ClientEnvironment.objects.update_or_create(
                company=company,
                defaults={
                    "is_active": True,
                },
            )
        )

        return client_environment

    # ------------------------------------------------------------------
    # Utilisateurs
    # ------------------------------------------------------------------

    @staticmethod
    def _create_user(
        *,
        email: str,
        last_name: str,
        first_name: str,
        company: Company,
    ) -> User:
        user, created = User.objects.update_or_create(
            email=email,
            defaults={
                "last_name": last_name,
                "first_name": first_name,
                "company": company,
                "is_active": True,
                "is_system_admin": False,
                "is_staff": False,
                "must_change_password": False,
            },
        )

        if created or not user.has_usable_password():
            user.set_password("Level2-Test-2026!")
            user.save()

        return user

    # ------------------------------------------------------------------
    # Environnement client
    # ------------------------------------------------------------------

    @staticmethod
    def _create_environment_membership(
        *,
        client_environment: ClientEnvironment,
        user: User,
        employment_type: CatalogValue,
    ) -> ClientEnvironmentMembership:
        membership, _ = (
            ClientEnvironmentMembership.objects
            .update_or_create(
                client_environment=client_environment,
                user=user,
                defaults={
                    "employment_type": employment_type,
                    "is_client_admin": False,
                    "is_client_admin_responsible": False,
                    "is_active": True,
                },
            )
        )

        membership.full_clean()
        membership.save()

        return membership

    # ------------------------------------------------------------------
    # Projet
    # ------------------------------------------------------------------

    def _create_project(
        self,
        *,
        company: Company,
        status: CatalogValue,
    ) -> Project:
        project, _ = Project.objects.update_or_create(
            reference=self.PROJECT_REFERENCE,
            defaults={
                "name": self.PROJECT_NAME,
                "company": company,
                "status": status,
                "is_active": True,
            },
        )

        project.full_clean()
        project.save()

        return project

    @staticmethod
    def _create_project_company(
        *,
        project: Project,
        company: Company,
    ) -> ProjectCompany:
        project_company, _ = (
            ProjectCompany.objects.get_or_create(
                project=project,
                company=company,
            )
        )

        project_company.full_clean()
        project_company.save()

        return project_company

    # ------------------------------------------------------------------
    # Affectations projet
    # ------------------------------------------------------------------

    @staticmethod
    def _create_project_membership(
        *,
        project: Project,
        user: User,
        role: CatalogValue,
        access_level: CatalogValue,
        responsible: bool,
    ) -> ProjectMembership:
        membership, _ = (
            ProjectMembership.objects.update_or_create(
                project=project,
                user=user,
                defaults={
                    "role": role,
                    "access_level": access_level,
                    "is_project_manager_responsible": (
                        responsible
                    ),
                    "is_active": True,
                },
            )
        )

        membership.full_clean()
        membership.save()

        return membership