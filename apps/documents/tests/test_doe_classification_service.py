

from __future__ import annotations

import json
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.client_configuration.models import (
    DoeTemplate,
    DoeTemplateFolder,
)
from apps.companies.models import Company
from apps.core.models import ClientEnvironment
from apps.documents.models import (
    Document,
    DocumentFolder,
    DocumentHistory,
    DoeClassificationProposal,
)
from apps.documents.services.document_service import (
    DocumentService,
)
from apps.documents.services.doe_classification_service import (
    DoeClassificationError,
    DoeClassificationService,
)
from apps.documents.services.doe_service import DoeService
from apps.documents.storage import FileSystemDocumentStorage
from apps.integrations.services.openai_services import (
    OpenAIIntegrationError,
)
from apps.projects.models import Project
from apps.users.models import User


class DoeClassificationServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Société test classement DOE",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.user = User.objects.create(
            company=cls.company,
            email="classement-doe@example.com",
            first_name="Jean",
            last_name="DOE",
        )

        cls.project_status_type = CatalogType.objects.create(
            code="T_DOE_AI_PROJECT_STATUS",
            label="Statut projet test classement DOE",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.document_type_catalog = CatalogType.objects.create(
            code="T_DOE_AI_DOCUMENT_TYPE",
            label="Type documentaire test classement DOE",
        )

        cls.document_status_catalog = CatalogType.objects.create(
            code="T_DOE_AI_DOCUMENT_STATUS",
            label="Statut documentaire test classement DOE",
        )

        cls.document_lifecycle_catalog = CatalogType.objects.create(
            code="T_DOE_AI_DOCUMENT_LIFECYCLE",
            label="Cycle documentaire test classement DOE",
        )

        cls.document_type = CatalogValue.objects.create(
            catalog_type=cls.document_type_catalog,
            code="NOTE",
            label="Note technique",
            sort_order=10,
        )

        cls.document_status = CatalogValue.objects.create(
            catalog_type=cls.document_status_catalog,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        cls.document_lifecycle = CatalogValue.objects.create(
            catalog_type=cls.document_lifecycle_catalog,
            code="ACTIVE",
            label="Actif",
            sort_order=10,
        )

    def setUp(self):
        self.project = Project.objects.create(
            company=self.company,
            reference=(
                f"PRJ-DOE-IA-{self._testMethodName[-8:].upper()}"
            ),
            name="Projet test classement DOE",
            status=self.project_status,
        )

        self.temporary_directory = TemporaryDirectory()

        self.document_service = DocumentService(
            storage=FileSystemDocumentStorage(
                self.temporary_directory.name
            )
        )

        self.doe_service = DoeService(
            document_service=self.document_service,
        )

        self.ai_service = Mock()

        self.service = DoeClassificationService(
            ai_service=self.ai_service,
        )

        self.source_root = DocumentFolder.objects.create(
            project=self.project,
            name="Documents source",
            sort_order=10,
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def create_source_document(
        self,
        *,
        title="Document DOE",
        folder=None,
        is_doe=True,
    ) -> Document:
        document = self.document_service.import_document(
            project=self.project,
            folder=folder or self.source_root,
            title=title,
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            content=BytesIO(
                b"Contenu documentaire confidentiel de test"
            ),
            original_filename=f"{title}.pdf",
            mime_type="application/pdf",
            user=self.user,
        )

        if is_doe:
            document.is_doe = True
            document.save(
                update_fields=[
                    "is_doe",
                    "updated_at",
                ]
            )

        return document

    def create_doe_template(self) -> DoeTemplate:
        template = DoeTemplate.objects.create(
            client_environment=self.client_environment,
            name="DOE type classement IA",
        )

        administrative = DoeTemplateFolder.objects.create(
            template=template,
            name="Administratif",
            sort_order=10,
        )

        DoeTemplateFolder.objects.create(
            template=template,
            parent=administrative,
            name="Procès-verbaux",
            sort_order=10,
        )

        return template

    def generate_template_doe(self):
        doe_template = self.create_doe_template()

        source_document = self.create_source_document(
            title="Compte rendu de chantier",
        )

        generation = self.doe_service.generate(
            project=self.project,
            user=self.user,
            doe_template=doe_template,
        )

        generated_document = Document.objects.get(
            project=self.project,
            is_doe_generated=True,
            doe_source_document=source_document,
        )

        target_folder = DocumentFolder.objects.get(
            project=self.project,
            name="Procès-verbaux",
            is_doe_generated=True,
        )

        return (
            generation,
            generated_document,
            target_folder,
        )

    def test_create_proposal_persists_recommendation(self):
        (
            generation,
            generated_document,
            target_folder,
        ) = self.generate_template_doe()

        self.ai_service.generate_text.return_value = json.dumps(
            {
                "classifications": [
                    {
                        "document_id": str(generated_document.pk),
                        "folder_id": str(target_folder.pk),
                        "confidence_percent": 87,
                        "reason": (
                            "Il s'agit d'un compte rendu "
                            "de chantier."
                        ),
                    },
                ],
            }
        )

        proposal = self.service.create_proposal(
            doe_generation=generation,
            user=self.user,
        )

        self.assertEqual(
            proposal.status,
            DoeClassificationProposal.Status.COMPLETED,
        )
        self.assertEqual(
            proposal.input_document_count,
            1,
        )

        item = proposal.items.get()

        self.assertEqual(
            item.document,
            generated_document,
        )
        self.assertEqual(
            item.proposed_folder,
            target_folder,
        )
        self.assertEqual(
            item.confidence_percent,
            87,
        )
        self.assertEqual(
            item.reason,
            "Il s'agit d'un compte rendu de chantier.",
        )
        self.assertEqual(
            item.status,
            item.Status.PENDING,
        )

    def test_request_contains_metadata_but_not_content(self):
        (
            generation,
            generated_document,
            target_folder,
        ) = self.generate_template_doe()

        self.ai_service.generate_text.return_value = json.dumps(
            {
                "classifications": [
                    {
                        "document_id": str(generated_document.pk),
                        "folder_id": str(target_folder.pk),
                        "confidence_percent": 70,
                        "reason": "Classement proposé.",
                    },
                ],
            }
        )

        self.service.create_proposal(
            doe_generation=generation,
            user=self.user,
        )

        self.ai_service.generate_text.assert_called_once()

        call_kwargs = (
            self.ai_service.generate_text.call_args.kwargs
        )

        payload = json.loads(call_kwargs["input_text"])

        self.assertEqual(
            payload["documents"][0]["title"],
            "Compte rendu de chantier",
        )
        self.assertEqual(
            payload["documents"][0]["extension"],
            ".pdf",
        )
        self.assertNotIn(
            "Contenu documentaire confidentiel de test",
            call_kwargs["input_text"],
        )
        self.assertEqual(
            call_kwargs["max_output_tokens"],
            4_000,
        )

    def test_invalid_json_creates_failed_proposal(self):
        (
            generation,
            _generated_document,
            _target_folder,
        ) = self.generate_template_doe()

        self.ai_service.generate_text.return_value = (
            "Réponse non structurée"
        )

        with self.assertRaises(DoeClassificationError):
            self.service.create_proposal(
                doe_generation=generation,
                user=self.user,
            )

        proposal = DoeClassificationProposal.objects.get(
            project=self.project,
        )

        self.assertEqual(
            proposal.status,
            DoeClassificationProposal.Status.FAILED,
        )
        self.assertEqual(
            proposal.input_document_count,
            1,
        )
        self.assertIn(
            "non exploitable",
            proposal.error_message,
        )
        self.assertFalse(
            proposal.items.exists()
        )

    def test_openai_error_creates_failed_proposal(self):
        (
            generation,
            _generated_document,
            _target_folder,
        ) = self.generate_template_doe()

        self.ai_service.generate_text.side_effect = (
            OpenAIIntegrationError(
                "La connexion au service OpenAI a échoué."
            )
        )

        with self.assertRaises(DoeClassificationError):
            self.service.create_proposal(
                doe_generation=generation,
                user=self.user,
            )

        proposal = DoeClassificationProposal.objects.get(
            project=self.project,
        )

        self.assertEqual(
            proposal.status,
            DoeClassificationProposal.Status.FAILED,
        )
        self.assertIn(
            "connexion au service OpenAI",
            proposal.error_message,
        )

    def test_unknown_folder_creates_unclassified_item(self):
        (
            generation,
            generated_document,
            _target_folder,
        ) = self.generate_template_doe()

        self.ai_service.generate_text.return_value = json.dumps(
            {
                "classifications": [
                    {
                        "document_id": str(generated_document.pk),
                        "folder_id": "00000000-0000-0000-0000-000000000000",
                        "confidence_percent": 130,
                        "reason": "Dossier inexistant.",
                    },
                ],
            }
        )

        proposal = self.service.create_proposal(
            doe_generation=generation,
            user=self.user,
        )

        item = proposal.items.get()

        self.assertIsNone(
            item.proposed_folder,
        )
        self.assertEqual(
            item.confidence_percent,
            100,
        )
        self.assertIn(
            "dossier proposé par l'IA est invalide",
            item.reason,
        )

    def create_pending_proposal(self):
        (
            generation,
            generated_document,
            proposed_folder,
        ) = self.generate_template_doe()

        self.ai_service.generate_text.return_value = json.dumps(
            {
                "classifications": [
                    {
                        "document_id": str(generated_document.pk),
                        "folder_id": str(proposed_folder.pk),
                        "confidence_percent": 85,
                        "reason": "Compte rendu à classer.",
                    },
                ],
            }
        )

        proposal = self.service.create_proposal(
            doe_generation=generation,
            user=self.user,
        )

        return (
            proposal,
            proposal.items.get(),
            generated_document,
            proposed_folder,
        )

    def test_apply_item_moves_document_and_records_review(self):
        (
            proposal,
            item,
            generated_document,
            _proposed_folder,
        ) = self.create_pending_proposal()

        corrected_folder = DocumentFolder.objects.get(
            project=self.project,
            name="Administratif",
            is_doe_generated=True,
        )

        self.service.apply_item(
            item=item,
            destination=corrected_folder,
            user=self.user,
        )

        generated_document.refresh_from_db()
        item.refresh_from_db()

        self.assertEqual(
            generated_document.folder,
            corrected_folder,
        )
        self.assertEqual(
            item.final_folder,
            corrected_folder,
        )
        self.assertEqual(
            item.status,
            item.Status.APPLIED,
        )
        self.assertEqual(
            item.reviewed_by,
            self.user,
        )
        self.assertIsNotNone(
            item.reviewed_at,
        )

        self.assertTrue(
            DocumentHistory.objects.filter(
                document=generated_document,
                action=DocumentHistory.Action.MOVED,
                user=self.user,
            ).exists()
        )

        self.assertEqual(
            proposal.items.count(),
            1,
        )

    def test_reject_item_keeps_document_in_to_sort_folder(self):
        (
            _proposal,
            item,
            generated_document,
            _proposed_folder,
        ) = self.create_pending_proposal()

        initial_folder = generated_document.folder

        self.service.reject_item(
            item=item,
            user=self.user,
        )

        generated_document.refresh_from_db()
        item.refresh_from_db()

        self.assertEqual(
            generated_document.folder,
            initial_folder,
        )
        self.assertEqual(
            item.status,
            item.Status.REJECTED,
        )
        self.assertIsNone(
            item.final_folder,
        )
        self.assertEqual(
            item.reviewed_by,
            self.user,
        )
        self.assertIsNotNone(
            item.reviewed_at,
        )

        self.assertFalse(
            DocumentHistory.objects.filter(
                document=generated_document,
                action=DocumentHistory.Action.MOVED,
            ).exists()
        )

    def test_applied_item_cannot_be_applied_twice(self):
        (
            _proposal,
            item,
            _generated_document,
            proposed_folder,
        ) = self.create_pending_proposal()

        self.service.apply_item(
            item=item,
            destination=proposed_folder,
            user=self.user,
        )

        with self.assertRaises(DoeClassificationError):
            self.service.apply_item(
                item=item,
                destination=proposed_folder,
                user=self.user,
            )

    def test_item_cannot_be_applied_to_source_folder(self):
        (
            _proposal,
            item,
            _generated_document,
            _proposed_folder,
        ) = self.create_pending_proposal()

        with self.assertRaises(DoeClassificationError):
            self.service.apply_item(
                item=item,
                destination=self.source_root,
                user=self.user,
            )