

from __future__ import annotations

from unittest.mock import Mock

from django.test import SimpleTestCase

from apps.documents.integrations import (
    DocumentCapability,
    DocumentIntegration,
    DocumentIntegrationRegistry,
    DocumentIntegrationResolver,
)
from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.integrations.models import ExternalIntegration
from django.test import SimpleTestCase, TestCase


class FakeOfficeIntegration(DocumentIntegration):
    provider_code = "FAKE_OFFICE"

    capabilities = frozenset(
        {
            DocumentCapability.OFFICE_EDIT,
            DocumentCapability.OFFICE_VIEW,
        }
    )

    OFFICE_MIME_TYPES = {
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument."
        "presentationml.presentation",
    }

    def supports(
        self,
        *,
        version,
        capability,
    ) -> bool:
        return (
            self.provides(capability)
            and version.mime_type in self.OFFICE_MIME_TYPES
        )

    def open(
        self,
        *,
        version,
        capability,
        user,
    ):
        return {
            "provider": self.provider_code,
            "capability": capability,
        }


class FakeCadIntegration(DocumentIntegration):
    provider_code = "FAKE_CAD"

    capabilities = frozenset(
        {
            DocumentCapability.CAD_VIEW,
        }
    )

    def supports(
        self,
        *,
        version,
        capability,
    ) -> bool:
        return (
            self.provides(capability)
            and version.mime_type == "application/acad"
        )

    def open(
        self,
        *,
        version,
        capability,
        user,
    ):
        return {
            "provider": self.provider_code,
            "capability": capability,
        }


class DocumentIntegrationRegistryTests(SimpleTestCase):

    def setUp(self):
        self.registry = DocumentIntegrationRegistry()

    def test_register_integration(self):
        integration = FakeOfficeIntegration()

        self.registry.register(integration)

        self.assertIs(
            self.registry.get("FAKE_OFFICE"),
            integration,
        )

    def test_provider_code_is_case_insensitive(self):
        integration = FakeOfficeIntegration()

        self.registry.register(integration)

        self.assertIs(
            self.registry.get("fake_office"),
            integration,
        )

    def test_duplicate_provider_is_rejected(self):
        self.registry.register(
            FakeOfficeIntegration()
        )

        with self.assertRaises(ValueError):
            self.registry.register(
                FakeOfficeIntegration()
            )

    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(LookupError):
            self.registry.get(
                "UNKNOWN"
            )

    def test_all_returns_registered_integrations(self):
        office = FakeOfficeIntegration()
        cad = FakeCadIntegration()

        self.registry.register(office)
        self.registry.register(cad)

        integrations = self.registry.all()

        self.assertEqual(
            len(integrations),
            2,
        )

        self.assertIn(
            office,
            integrations,
        )

        self.assertIn(
            cad,
            integrations,
        )

    def test_clear_registry(self):
        self.registry.register(
            FakeOfficeIntegration()
        )

        self.registry.clear()

        self.assertEqual(
            self.registry.all(),
            (),
        )


class DocumentIntegrationResolverTests(SimpleTestCase):

    def setUp(self):
        self.registry = DocumentIntegrationRegistry()

        self.office = FakeOfficeIntegration()
        self.cad = FakeCadIntegration()

        self.registry.register(
            self.office
        )

        self.registry.register(
            self.cad
        )

        self.resolver = DocumentIntegrationResolver(
            integration_registry=self.registry
        )

    @staticmethod
    def make_version(
        mime_type: str,
    ):
        version = Mock()
        version.mime_type = mime_type
        return version

    def test_resolve_office_edit(self):
        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        integration = self.resolver.resolve(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
        )

        self.assertIs(
            integration,
            self.office,
        )

    def test_resolve_office_view(self):
        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )

        integration = self.resolver.resolve(
            version=version,
            capability=DocumentCapability.OFFICE_VIEW,
        )

        self.assertIs(
            integration,
            self.office,
        )

    def test_resolve_cad_view(self):
        version = self.make_version(
            "application/acad"
        )

        integration = self.resolver.resolve(
            version=version,
            capability=DocumentCapability.CAD_VIEW,
        )

        self.assertIs(
            integration,
            self.cad,
        )

    def test_explicit_provider_is_used(self):
        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        integration = self.resolver.resolve(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            provider_code="FAKE_OFFICE",
        )

        self.assertIs(
            integration,
            self.office,
        )

    def test_provider_without_capability_is_rejected(self):
        version = self.make_version(
            "application/acad"
        )

        with self.assertRaises(LookupError):
            self.resolver.resolve(
                version=version,
                capability=DocumentCapability.CAD_VIEW,
                provider_code="FAKE_OFFICE",
            )

    def test_provider_not_supporting_document_is_rejected(self):
        version = self.make_version(
            "application/pdf"
        )

        with self.assertRaises(LookupError):
            self.resolver.resolve(
                version=version,
                capability=DocumentCapability.OFFICE_VIEW,
                provider_code="FAKE_OFFICE",
            )

    def test_no_compatible_integration_is_rejected(self):
        version = self.make_version(
            "application/pdf"
        )

        with self.assertRaises(LookupError):
            self.resolver.resolve(
                version=version,
                capability=DocumentCapability.CAD_VIEW,
            )
            
class DocumentIntegrationCompanyResolverTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société intégrations GED",
        )

        cls.client_environment = ClientEnvironment.objects.create(
            company=cls.company,
        )

        # --------------------------------------------------------------
        # Catalogues
        # --------------------------------------------------------------

        cls.service_type_catalog = CatalogType.objects.create(
            code="INTEGRATION_SERVICE_TYPE",
            label="Type de service",
        )

        cls.provider_catalog = CatalogType.objects.create(
            code="INTEGRATION_PROVIDER",
            label="Fournisseur",
        )

        cls.connection_status_catalog = CatalogType.objects.create(
            code="INTEGRATION_CONNECTION_STATUS",
            label="État de connexion",
        )

        # --------------------------------------------------------------
        # Types de service
        # --------------------------------------------------------------

        cls.office_service = CatalogValue.objects.create(
            catalog_type=cls.service_type_catalog,
            code="OFFICE",
            label="Suite bureautique",
            sort_order=10,
        )

        cls.cad_service = CatalogValue.objects.create(
            catalog_type=cls.service_type_catalog,
            code="CAD_VIEWER",
            label="Visualisation CAO",
            sort_order=20,
        )

        # --------------------------------------------------------------
        # Fournisseurs
        # --------------------------------------------------------------

        cls.office_provider = CatalogValue.objects.create(
            catalog_type=cls.provider_catalog,
            code="FAKE_OFFICE",
            label="Fake Office",
            sort_order=10,
        )

        cls.cad_provider = CatalogValue.objects.create(
            catalog_type=cls.provider_catalog,
            code="FAKE_CAD",
            label="Fake CAD",
            sort_order=20,
        )

        # Provider volontairement sans adaptateur
        cls.unknown_provider = CatalogValue.objects.create(
            catalog_type=cls.provider_catalog,
            code="UNKNOWN_PROVIDER",
            label="Provider inconnu",
            sort_order=30,
        )

        # --------------------------------------------------------------
        # États de connexion
        # --------------------------------------------------------------

        cls.connected_status = CatalogValue.objects.create(
            catalog_type=cls.connection_status_catalog,
            code="CONNECTED",
            label="Connectée",
            sort_order=10,
        )

        cls.configured_status = CatalogValue.objects.create(
            catalog_type=cls.connection_status_catalog,
            code="CONFIGURED",
            label="Configurée",
            sort_order=20,
        )

    def setUp(self):
        self.registry = DocumentIntegrationRegistry()

        self.office = FakeOfficeIntegration()
        self.cad = FakeCadIntegration()

        self.registry.register(self.office)
        self.registry.register(self.cad)

        self.resolver = DocumentIntegrationResolver(
            integration_registry=self.registry
        )

    @staticmethod
    def make_version(mime_type: str):
        version = Mock()
        version.mime_type = mime_type
        return version

    def create_external_integration(
        self,
        *,
        service_type,
        provider,
        connection_status=None,
        priority=100,
        is_active=True,
        code=None,
    ):
        return ExternalIntegration.objects.create(
            client_environment=self.client_environment,
            service_type=service_type,
            provider=provider,
            connection_status=(
                connection_status
                or self.connected_status
            ),
            code=(
                code
                or f"TEST_{provider.code}_{priority}"
            ),
            name=f"Test {provider.label}",
            priority=priority,
            is_active=is_active,
        )

    def test_resolve_office_for_company(self):
        self.create_external_integration(
            service_type=self.office_service,
            provider=self.office_provider,
        )

        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        integration = self.resolver.resolve_for_company(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            company=self.company,
        )

        self.assertIs(
            integration,
            self.office,
        )

    def test_resolve_cad_for_company(self):
        self.create_external_integration(
            service_type=self.cad_service,
            provider=self.cad_provider,
        )

        version = self.make_version(
            "application/acad"
        )

        integration = self.resolver.resolve_for_company(
            version=version,
            capability=DocumentCapability.CAD_VIEW,
            company=self.company,
        )

        self.assertIs(
            integration,
            self.cad,
        )

    def test_inactive_integration_is_ignored(self):
        self.create_external_integration(
            service_type=self.office_service,
            provider=self.office_provider,
            is_active=False,
        )

        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        with self.assertRaises(LookupError):
            self.resolver.resolve_for_company(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
                company=self.company,
            )

    def test_not_connected_integration_is_ignored(self):
        self.create_external_integration(
            service_type=self.office_service,
            provider=self.office_provider,
            connection_status=self.configured_status,
        )

        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        with self.assertRaises(LookupError):
            self.resolver.resolve_for_company(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
                company=self.company,
            )

    def test_unknown_provider_is_skipped(self):
        self.create_external_integration(
            service_type=self.office_service,
            provider=self.unknown_provider,
            priority=10,
        )

        self.create_external_integration(
            service_type=self.office_service,
            provider=self.office_provider,
            priority=20,
        )

        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        integration = self.resolver.resolve_for_company(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            company=self.company,
        )

        self.assertIs(
            integration,
            self.office,
        )

    def test_priority_is_respected(self):
        second_office = FakeOfficeIntegration()
        second_office.provider_code = "SECOND_OFFICE"

        self.registry.register(
            second_office
        )

        second_provider = CatalogValue.objects.create(
            catalog_type=self.provider_catalog,
            code="SECOND_OFFICE",
            label="Second Office",
            sort_order=40,
        )

        self.create_external_integration(
            service_type=self.office_service,
            provider=second_provider,
            priority=10,
        )

        self.create_external_integration(
            service_type=self.office_service,
            provider=self.office_provider,
            priority=20,
        )

        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        integration = self.resolver.resolve_for_company(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            company=self.company,
        )

        self.assertIs(
            integration,
            second_office,
        )

    def test_company_without_client_environment_is_rejected(self):
        company = Company.objects.create(
            name="Société sans environnement",
        )

        version = self.make_version(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        with self.assertRaises(LookupError):
            self.resolver.resolve_for_company(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
                company=company,
            )