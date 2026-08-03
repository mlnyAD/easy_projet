

from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.licenses.exceptions import (
    LicenseDateError,
    LicenseReferenceAlreadyExistsError,
)
from apps.licenses.models import License
from apps.licenses.services import LicenseService
from common.constants.license import (
    DEFAULT_LICENSE_PROJECT_CAPACITY,
)


class LicenseServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.company = Company.objects.create(
            name="Société cliente",
            is_active=True,
        )

        cls.other_company = Company.objects.create(
            name="Autre société",
            is_active=True,
        )

        license_status_catalog = (
            CatalogType.objects.create(
                code="LICENSE_STATUS",
                label="Statut de la licence",
                is_active=True,
            )
        )

        cls.waiting_status = (
            CatalogValue.objects.create(
                catalog_type=license_status_catalog,
                code="WAITING",
                label="En attente",
                is_active=True,
            )
        )

    def create_license(
        self,
        *,
        company: Company | None = None,
        reference: str = "CMD-2026-001",
        project_capacity: int = (
            DEFAULT_LICENSE_PROJECT_CAPACITY
        ),
        expiration_date: date | None = None,
    ) -> License:
        return LicenseService.create_license(
            company=company or self.company,
            reference=reference,
            granted_at=date(2026, 8, 2),
            expiration_date=expiration_date,
            project_capacity=project_capacity,
        )

    def test_first_license_creates_client_environment(self):
        self.assertFalse(
            ClientEnvironment.objects.filter(
                company=self.company,
            ).exists()
        )

        license_instance = self.create_license()

        environment = ClientEnvironment.objects.get(
            company=self.company,
        )

        self.assertEqual(
            license_instance.client_environment,
            environment,
        )
        self.assertTrue(environment.is_active)

    def test_second_license_reuses_client_environment(self):
        first_license = self.create_license(
            reference="CMD-2026-001",
        )

        second_license = self.create_license(
            reference="CMD-2026-002",
        )

        self.assertEqual(
            first_license.client_environment,
            second_license.client_environment,
        )

        self.assertEqual(
            ClientEnvironment.objects.filter(
                company=self.company,
            ).count(),
            1,
        )

    def test_license_is_created_with_waiting_status(self):
        license_instance = self.create_license()

        self.assertEqual(
            license_instance.status,
            self.waiting_status,
        )

    def test_reference_is_trimmed(self):
        license_instance = self.create_license(
            reference="  DEV-2026-010  ",
        )

        self.assertEqual(
            license_instance.reference,
            "DEV-2026-010",
        )

    def test_default_project_capacity_is_applied(self):
        license_instance = self.create_license()

        self.assertEqual(
            license_instance.project_capacity,
            DEFAULT_LICENSE_PROJECT_CAPACITY,
        )

    def test_custom_project_capacity_is_supported(self):
        license_instance = self.create_license(
            project_capacity=10,
        )

        self.assertEqual(
            license_instance.project_capacity,
            10,
        )

    def test_expiration_date_is_saved(self):
        expiration_date = date(2027, 8, 2)

        license_instance = self.create_license(
            expiration_date=expiration_date,
        )

        self.assertEqual(
            license_instance.expiration_date,
            expiration_date,
        )

    def test_expiration_before_granted_at_is_rejected(self):
        with self.assertRaises(LicenseDateError):
            self.create_license(
                expiration_date=date(2026, 8, 1),
            )

        self.assertEqual(
            License.objects.count(),
            0,
        )
        self.assertEqual(
            ClientEnvironment.objects.count(),
            0,
        )

    def test_duplicate_reference_is_rejected_for_same_environment(
        self,
    ):
        self.create_license(
            reference="CMD-2026-001",
        )

        with self.assertRaises(
            LicenseReferenceAlreadyExistsError
        ):
            self.create_license(
                reference="CMD-2026-001",
            )

        self.assertEqual(
            License.objects.count(),
            1,
        )

    def test_same_reference_is_allowed_for_another_company(self):
        first_license = self.create_license(
            company=self.company,
            reference="CMD-2026-001",
        )

        second_license = self.create_license(
            company=self.other_company,
            reference="CMD-2026-001",
        )

        self.assertNotEqual(
            first_license.client_environment,
            second_license.client_environment,
        )

        self.assertEqual(
            License.objects.count(),
            2,
        )