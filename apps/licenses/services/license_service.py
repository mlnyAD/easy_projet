

from __future__ import annotations

from datetime import date

from django.db import transaction

from apps.catalogs.services import CatalogService
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.licenses.exceptions import (
    LicenseDateError,
    LicenseReferenceAlreadyExistsError,
)
from apps.licenses.models import License
from common.constants.license import (
    DEFAULT_LICENSE_PROJECT_CAPACITY,
)


class LicenseService:
    """
    Point d'entrée métier pour la gestion des licences.

    Toute source autorisée doit utiliser ce service :
    interface administrateur système, workflow commercial
    ou futur paiement en ligne.
    """

    @staticmethod
    @transaction.atomic
    def create_license(
        *,
        company: Company,
        reference: str,
        granted_at: date,
        expiration_date: date | None = None,
        project_capacity: int = (
            DEFAULT_LICENSE_PROJECT_CAPACITY
        ),
    ) -> License:
        """
        Crée une licence pour une société.

        Lors de la première licence, le ClientEnvironment
        de la société est créé automatiquement.
        """

        if not isinstance(company, Company):
            raise TypeError(
                "company doit être une instance de Company."
            )

        normalized_reference = reference.strip()

        if (
            expiration_date is not None
            and expiration_date < granted_at
        ):
            raise LicenseDateError()

        # Le verrou évite que deux créations simultanées produisent
        # deux tentatives concurrentes de ClientEnvironment.
        locked_company = (
            Company.objects
            .select_for_update()
            .get(pk=company.pk)
        )

        client_environment, _created = (
            ClientEnvironment.objects.get_or_create(
                company=locked_company,
                defaults={
                    "is_active": True,
                },
            )
        )

        if License.objects.filter(
            client_environment=client_environment,
            reference=normalized_reference,
        ).exists():
            raise LicenseReferenceAlreadyExistsError(
                normalized_reference,
            )

        waiting_status = CatalogService.get_value(
            "LICENSE_STATUS",
            "WAITING",
        )

        license_instance = License(
            client_environment=client_environment,
            reference=normalized_reference,
            status=waiting_status,
            project_capacity=project_capacity,
            granted_at=granted_at,
            expiration_date=expiration_date,
        )

        license_instance.full_clean()
        license_instance.save()

        return license_instance