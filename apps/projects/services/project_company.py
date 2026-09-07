

"""
Services métier des sociétés participantes aux projets.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.companies.models import Company
from apps.projects.models import Project, ProjectCompany


class ProjectCompanyService:
    """
    Gère les sociétés participant à un projet.

    La société responsable du projet est toujours considérée
    comme participante et ne peut pas être retirée.
    """

    @staticmethod
    @transaction.atomic
    def ensure_responsible_company(
        project: Project,
    ) -> ProjectCompany:
        """
        Garantit la présence de la société responsable
        parmi les sociétés participantes.
        """
        participation, _ = ProjectCompany.objects.get_or_create(
            project=project,
            company=project.company,
        )

        return participation

    @staticmethod
    @transaction.atomic
    def add_company(
        project: Project,
        company: Company,
    ) -> ProjectCompany:
        """
        Ajoute une société au projet.

        L'opération est idempotente.
        """
        participation, _ = ProjectCompany.objects.get_or_create(
            project=project,
            company=company,
        )

        return participation

    @staticmethod
    @transaction.atomic
    def remove_company(
        project: Project,
        company: Company,
    ) -> None:
        """
        Retire une société participante du projet.

        La société responsable du projet ne peut pas être retirée.
        """
        if company.pk == project.company_id:
            raise ValidationError(
                "La société responsable du projet "
                "ne peut pas être retirée."
            )

        ProjectCompany.objects.filter(
            project=project,
            company=company,
        ).delete()