

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessage,
    CommunicationMessageAttachment,
    CommunicationMessageRecipient,
)
from apps.core.models import ClientEnvironment
from apps.documents.models import (
    Document,
    DocumentFolder,
    DocumentVersion,
)
from apps.projects.models import (
    Project,
    ProjectExternalParticipant,
    ProjectMembership,
)
from apps.users.models import User
from apps.communications.services import CommunicationService


class CommunicationModelTests(TestCase):
    """
    Tests du noyau métier Communications.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Sociétés
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société communication",
        )

        cls.other_company = Company.objects.create(
            name="Autre société communication",
        )

        # --------------------------------------------------------------
        # Environnements clients
        # --------------------------------------------------------------

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.other_client_environment = (
            ClientEnvironment.objects.create(
                company=cls.other_company,
            )
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = (
            CatalogType.objects.create(
                code="USER_GLOBAL_ROLE",
                label="Rôle global utilisateur",
            )
        )

        cls.access_level_type = (
            CatalogType.objects.create(
                code="COMMUNICATION_ACCESS_LEVEL",
                label="Niveau accès communications",
            )
        )

        cls.system_admin_role = (
            CatalogValue.objects.create(
                catalog_type=cls.global_role_type,
                code="SYSTEM_ADMIN",
                label="Administrateur système",
                sort_order=10,
            )
        )

        cls.access_level = (
            CatalogValue.objects.create(
                catalog_type=cls.access_level_type,
                code="STANDARD",
                label="Standard",
                sort_order=10,
            )
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.user = User.objects.create(
            company=cls.company,
            email="communication-user@example.com",
            first_name="Jean",
            last_name="Utilisateur",
            global_role=cls.system_admin_role,
            access_level=cls.access_level,
        )

        cls.recipient_user = User.objects.create(
            company=cls.company,
            email="communication-recipient@example.com",
            first_name="Paul",
            last_name="Destinataire",
            global_role=cls.system_admin_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = (
            CatalogType.objects.create(
                code="PROJECT_STATUS",
                label="Statut projet",
            )
        )

        cls.project_status = (
            CatalogValue.objects.create(
                catalog_type=cls.project_status_type,
                code="IN_PROGRESS",
                label="En cours",
                sort_order=10,
                is_default=True,
            )
        )

        # --------------------------------------------------------------
        # Niveau accès intervenant externe
        # --------------------------------------------------------------

        cls.external_access_type = (
            CatalogType.objects.create(
                code="PROJECT_EXTERNAL_ACCESS",
                label="Accès participant externe",
            )
        )

        cls.external_access = (
            CatalogValue.objects.create(
                catalog_type=cls.external_access_type,
                code="STANDARD",
                label="Standard",
                sort_order=10,
                is_default=True,
            )
        )

        # --------------------------------------------------------------
        # Projets
        # --------------------------------------------------------------

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-COM-001",
            name="Projet communication",
            status=cls.project_status,
        )

        cls.other_project = Project.objects.create(
            company=cls.other_company,
            reference="PRJ-COM-002",
            name="Autre projet communication",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Intervenants externes
        # --------------------------------------------------------------

        cls.external_participant = (
            ProjectExternalParticipant.objects.create(
                project=cls.project,
                last_name="DUPONT",
                first_name="Pierre",
                email="pierre.dupont@example.com",
                company_name="Bureau de contrôle",
                access_level=cls.external_access,
            )
        )

        cls.other_external_participant = (
            ProjectExternalParticipant.objects.create(
                project=cls.other_project,
                last_name="MARTIN",
                first_name="Julie",
                email="julie.martin@example.com",
                company_name="Entreprise externe",
                access_level=cls.external_access,
            )
        )

        # --------------------------------------------------------------
        # Conversation
        # --------------------------------------------------------------

        cls.conversation = (
            CommunicationConversation.objects.create(
                project=cls.project,
                title="Conversation principale",
                created_by=cls.user,
            )
        )

        # --------------------------------------------------------------
        # Catalogues documentaires
        # --------------------------------------------------------------

        cls.document_type_type = (
            CatalogType.objects.create(
                code="DOCUMENT_TYPE",
                label="Type documentaire",
            )
        )

        cls.document_status_type = (
            CatalogType.objects.create(
                code="DOCUMENT_STATUS",
                label="Statut documentaire",
            )
        )

        cls.document_lifecycle_type = (
            CatalogType.objects.create(
                code="DOCUMENT_LIFECYCLE",
                label="Cycle documentaire",
            )
        )

        cls.document_type = (
            CatalogValue.objects.create(
                catalog_type=cls.document_type_type,
                code="OTHER",
                label="Autre",
                sort_order=10,
            )
        )

        cls.document_status = (
            CatalogValue.objects.create(
                catalog_type=cls.document_status_type,
                code="ACTIVE",
                label="Actif",
                sort_order=10,
            )
        )

        cls.document_lifecycle = (
            CatalogValue.objects.create(
                catalog_type=cls.document_lifecycle_type,
                code="CURRENT",
                label="Courant",
                sort_order=10,
            )
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def create_internal_message(self):
        return CommunicationMessage.objects.create(
            conversation=self.conversation,
            origin=CommunicationMessage.Origin.INTERNAL,
            author=self.user,
            body="Message de test.",
        )

    def create_document_version(
        self,
        *,
        project=None,
        storage_suffix="1",
    ):
        if project is None:
            project = self.project

        folder = DocumentFolder.objects.create(
            project=project,
            name=f"Dossier {storage_suffix}",
        )

        document = Document.objects.create(
            project=project,
            folder=folder,
            title=f"Document {storage_suffix}",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            created_by=self.user,
        )

        return DocumentVersion.objects.create(
            document=document,
            version_number=1,
            original_filename=f"document-{storage_suffix}.bin",
            storage_key=f"tests/document-{storage_suffix}.bin",
            mime_type="application/octet-stream",
            file_size=123,
            checksum=(
                "a" * 64
            ),
            created_by=self.user,
        )

    # ------------------------------------------------------------------
    # Message
    # ------------------------------------------------------------------

    def test_internal_message_requires_author(self):
        message = CommunicationMessage(
            conversation=self.conversation,
            origin=CommunicationMessage.Origin.INTERNAL,
            body="Message sans auteur.",
        )

        with self.assertRaises(
            ValidationError
        ):
            message.full_clean()

    def test_imported_email_requires_sender_email(self):
        message = CommunicationMessage(
            conversation=self.conversation,
            origin=(
                CommunicationMessage.Origin.IMPORTED_EMAIL
            ),
            imported_by=self.user,
            body="Mail importé.",
        )

        with self.assertRaises(
            ValidationError
        ):
            message.full_clean()

    def test_imported_email_requires_imported_by(self):
        message = CommunicationMessage(
            conversation=self.conversation,
            origin=(
                CommunicationMessage.Origin.IMPORTED_EMAIL
            ),
            sender_email="external@example.com",
            body="Mail importé.",
        )

        with self.assertRaises(
            ValidationError
        ):
            message.full_clean()

    def test_imported_email_is_valid(self):
        message = CommunicationMessage(
            conversation=self.conversation,
            origin=(
                CommunicationMessage.Origin.IMPORTED_EMAIL
            ),
            sender_name="Pierre Dupont",
            sender_email="pierre.dupont@example.com",
            imported_by=self.user,
            body="Mail importé volontairement.",
        )

        message.full_clean()

    # ------------------------------------------------------------------
    # Destinataires
    # ------------------------------------------------------------------

    def test_internal_recipient_is_valid(self):
        message = self.create_internal_message()

        recipient = CommunicationMessageRecipient(
            message=message,
            user=self.recipient_user,
            channel=(
                CommunicationMessageRecipient.Channel.INTERNAL
            ),
        )

        recipient.full_clean()

    def test_external_email_recipient_is_valid(self):
        message = self.create_internal_message()

        recipient = CommunicationMessageRecipient(
            message=message,
            external_participant=(
                self.external_participant
            ),
            destination_email=(
                self.external_participant.email
            ),
            channel=(
                CommunicationMessageRecipient.Channel.EMAIL
            ),
        )

        recipient.full_clean()

    def test_internal_channel_requires_user(self):
        message = self.create_internal_message()

        recipient = CommunicationMessageRecipient(
            message=message,
            external_participant=(
                self.external_participant
            ),
            destination_email=(
                self.external_participant.email
            ),
            channel=(
                CommunicationMessageRecipient.Channel.INTERNAL
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            recipient.full_clean()

    def test_email_channel_requires_destination_email(self):
        message = self.create_internal_message()

        recipient = CommunicationMessageRecipient(
            message=message,
            external_participant=(
                self.external_participant
            ),
            channel=(
                CommunicationMessageRecipient.Channel.EMAIL
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            recipient.full_clean()

    def test_external_recipient_must_belong_to_same_project(self):
        message = self.create_internal_message()

        recipient = CommunicationMessageRecipient(
            message=message,
            external_participant=(
                self.other_external_participant
            ),
            destination_email=(
                self.other_external_participant.email
            ),
            channel=(
                CommunicationMessageRecipient.Channel.EMAIL
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            recipient.full_clean()

    def test_recipient_cannot_have_two_recipient_types(self):
        message = self.create_internal_message()

        recipient = CommunicationMessageRecipient(
            message=message,
            user=self.recipient_user,
            external_participant=(
                self.external_participant
            ),
            destination_email=(
                self.external_participant.email
            ),
            channel=(
                CommunicationMessageRecipient.Channel.EMAIL
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            recipient.full_clean()

    # ------------------------------------------------------------------
    # Pièces jointes
    # ------------------------------------------------------------------

    def test_uploaded_file_attachment_is_valid(self):
        message = self.create_internal_message()

        uploaded_file = SimpleUploadedFile(
            name="archive.xyz",
            content=b"contenu test",
            content_type="application/octet-stream",
        )

        attachment = CommunicationMessageAttachment(
            message=message,
            uploaded_file=uploaded_file,
            original_filename="archive.xyz",
            mime_type="application/octet-stream",
            uploaded_by=self.user,
        )

        attachment.full_clean()

    def test_document_version_attachment_is_valid(self):
        message = self.create_internal_message()

        version = self.create_document_version(
            storage_suffix="same-project"
        )

        attachment = CommunicationMessageAttachment(
            message=message,
            document_version=version,
            uploaded_by=self.user,
        )

        attachment.full_clean()

    def test_attachment_requires_exactly_one_source(self):
        message = self.create_internal_message()

        attachment = CommunicationMessageAttachment(
            message=message,
            uploaded_by=self.user,
        )

        with self.assertRaises(
            ValidationError
        ):
            attachment.full_clean()

    def test_attachment_rejects_two_sources(self):
        message = self.create_internal_message()

        version = self.create_document_version(
            storage_suffix="double-source"
        )

        uploaded_file = SimpleUploadedFile(
            name="archive.xyz",
            content=b"contenu test",
            content_type="application/octet-stream",
        )

        attachment = CommunicationMessageAttachment(
            message=message,
            uploaded_file=uploaded_file,
            document_version=version,
            uploaded_by=self.user,
        )

        with self.assertRaises(
            ValidationError
        ):
            attachment.full_clean()

    def test_document_attachment_must_belong_to_same_project(self):
        message = self.create_internal_message()

        version = self.create_document_version(
            project=self.other_project,
            storage_suffix="other-project",
        )

        attachment = CommunicationMessageAttachment(
            message=message,
            document_version=version,
            uploaded_by=self.user,
        )

        with self.assertRaises(
            ValidationError
        ):
            attachment.full_clean()

class CommunicationServiceTests(TestCase):
    """
    Tests du service métier Communications.
    """

    @classmethod
    def setUpTestData(cls):
        # --------------------------------------------------------------
        # Société et environnement
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société service communication",
        )

        cls.other_company = Company.objects.create(
            name="Autre société service communication",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        cls.other_client_environment = (
            ClientEnvironment.objects.create(
                company=cls.other_company,
            )
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = CatalogType.objects.create(
            code="USER_GLOBAL_ROLE",
            label="Rôle global utilisateur",
        )

        cls.access_level_type = CatalogType.objects.create(
            code="COMMUNICATION_SERVICE_ACCESS",
            label="Accès service communication",
        )

        cls.system_admin_role = CatalogValue.objects.create(
            catalog_type=cls.global_role_type,
            code="SYSTEM_ADMIN",
            label="Administrateur système",
            sort_order=10,
        )

        cls.access_level = CatalogValue.objects.create(
            catalog_type=cls.access_level_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Rôle projet
        # --------------------------------------------------------------

        cls.project_role_type = CatalogType.objects.create(
            code="USER_PROJECT_ROLE",
            label="Rôle sur projet",
        )

        cls.project_role = CatalogValue.objects.create(
            catalog_type=cls.project_role_type,
            code="USER",
            label="Utilisateur",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Niveau d'accès externe
        # --------------------------------------------------------------

        cls.external_access_type = CatalogType.objects.create(
            code="PROJECT_EXTERNAL_ACCESS",
            label="Accès participant externe",
        )

        cls.external_access = CatalogValue.objects.create(
            catalog_type=cls.external_access_type,
            code="STANDARD",
            label="Standard",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = CatalogType.objects.create(
            code="PROJECT_STATUS",
            label="Statut projet",
        )

        cls.project_status = CatalogValue.objects.create(
            catalog_type=cls.project_status_type,
            code="IN_PROGRESS",
            label="En cours",
            sort_order=10,
        )

        # --------------------------------------------------------------
        # Utilisateurs
        # --------------------------------------------------------------

        cls.author = User.objects.create(
            company=cls.company,
            email="service-author@example.com",
            first_name="Jean",
            last_name="Auteur",
            global_role=cls.system_admin_role,
            access_level=cls.access_level,
        )

        cls.recipient = User.objects.create(
            company=cls.company,
            email="service-recipient@example.com",
            first_name="Paul",
            last_name="Destinataire",
            global_role=cls.system_admin_role,
            access_level=cls.access_level,
        )

        cls.other_user = User.objects.create(
            company=cls.other_company,
            email="service-other@example.com",
            first_name="Marie",
            last_name="Externe",
            global_role=cls.system_admin_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Projets
        # --------------------------------------------------------------

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-SRV-001",
            name="Projet service communication",
            status=cls.project_status,
        )

        cls.other_project = Project.objects.create(
            company=cls.other_company,
            reference="PRJ-SRV-002",
            name="Autre projet service communication",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Affectation interne
        # --------------------------------------------------------------

        cls.membership = ProjectMembership.objects.create(
            project=cls.project,
            user=cls.recipient,
            role=cls.project_role,
        )

        # --------------------------------------------------------------
        # Participants externes
        # --------------------------------------------------------------

        cls.external_participant = (
            ProjectExternalParticipant.objects.create(
                project=cls.project,
                last_name="DUPONT",
                first_name="Pierre",
                email="pierre.service@example.com",
                company_name="Bureau de contrôle",
                access_level=cls.external_access,
            )
        )

        cls.other_external_participant = (
            ProjectExternalParticipant.objects.create(
                project=cls.other_project,
                last_name="MARTIN",
                first_name="Julie",
                email="julie.service@example.com",
                company_name="Entreprise externe",
                access_level=cls.external_access,
            )
        )

        # --------------------------------------------------------------
        # Conversation
        # --------------------------------------------------------------

        cls.conversation = (
            CommunicationConversation.objects.create(
                project=cls.project,
                title="Conversation service",
                created_by=cls.author,
            )
        )

    # ------------------------------------------------------------------
    # Message interne
    # ------------------------------------------------------------------

    def test_send_internal_message_creates_message(self):
        message = (
            CommunicationService.send_internal_message(
                conversation=self.conversation,
                author=self.author,
                body="Message interne.",
                recipients=[
                    self.recipient,
                ],
            )
        )

        self.assertEqual(
            message.body,
            "Message interne.",
        )

        self.assertEqual(
            message.author,
            self.author,
        )

        self.assertEqual(
            message.origin,
            CommunicationMessage.Origin.INTERNAL,
        )

    def test_send_internal_message_creates_distribution(self):
        message = (
            CommunicationService.send_internal_message(
                conversation=self.conversation,
                author=self.author,
                body="Message interne.",
                recipients=[
                    self.recipient,
                ],
            )
        )

        distribution = (
            message.recipients.get()
        )

        self.assertEqual(
            distribution.user,
            self.recipient,
        )

        self.assertEqual(
            distribution.channel,
            CommunicationMessageRecipient.Channel.INTERNAL,
        )

        self.assertEqual(
            distribution.status,
            CommunicationMessageRecipient.Status.PENDING,
        )

    def test_send_internal_message_removes_duplicates(self):
        message = (
            CommunicationService.send_internal_message(
                conversation=self.conversation,
                author=self.author,
                body="Message sans doublon.",
                recipients=[
                    self.recipient,
                    self.recipient,
                ],
            )
        )

        self.assertEqual(
            message.recipients.count(),
            1,
        )

    def test_send_internal_message_requires_recipient(self):
        with self.assertRaises(
            ValidationError
        ):
            CommunicationService.send_internal_message(
                conversation=self.conversation,
                author=self.author,
                body="Message.",
                recipients=[],
            )

    def test_send_internal_message_rejects_empty_body(self):
        with self.assertRaises(
            ValidationError
        ):
            CommunicationService.send_internal_message(
                conversation=self.conversation,
                author=self.author,
                body="   ",
                recipients=[
                    self.recipient,
                ],
            )

    def test_send_internal_message_rejects_non_member(self):
        with self.assertRaises(
            ValidationError
        ):
            CommunicationService.send_internal_message(
                conversation=self.conversation,
                author=self.author,
                body="Message.",
                recipients=[
                    self.other_user,
                ],
            )

    # ------------------------------------------------------------------
    # Message email
    # ------------------------------------------------------------------

    def test_send_email_message_creates_message(self):
        message = (
            CommunicationService.send_email_message(
                conversation=self.conversation,
                author=self.author,
                body="Message externe.",
                recipients=[
                    self.external_participant,
                ],
            )
        )

        self.assertEqual(
            message.body,
            "Message externe.",
        )

        self.assertEqual(
            message.author,
            self.author,
        )

    def test_send_email_message_creates_email_distribution(self):
        message = (
            CommunicationService.send_email_message(
                conversation=self.conversation,
                author=self.author,
                body="Message externe.",
                recipients=[
                    self.external_participant,
                ],
            )
        )

        distribution = (
            message.recipients.get()
        )

        self.assertEqual(
            distribution.external_participant,
            self.external_participant,
        )

        self.assertEqual(
            distribution.destination_email,
            self.external_participant.email,
        )

        self.assertEqual(
            distribution.channel,
            CommunicationMessageRecipient.Channel.EMAIL,
        )

        self.assertEqual(
            distribution.status,
            CommunicationMessageRecipient.Status.PENDING,
        )

    def test_send_email_message_removes_duplicates(self):
        message = (
            CommunicationService.send_email_message(
                conversation=self.conversation,
                author=self.author,
                body="Message externe.",
                recipients=[
                    self.external_participant,
                    self.external_participant,
                ],
            )
        )

        self.assertEqual(
            message.recipients.count(),
            1,
        )

    def test_send_email_message_rejects_other_project(self):
        with self.assertRaises(
            ValidationError
        ):
            CommunicationService.send_email_message(
                conversation=self.conversation,
                author=self.author,
                body="Message externe.",
                recipients=[
                    self.other_external_participant,
                ],
            )

    def test_send_email_message_rejects_inactive_participant(self):
        self.external_participant.is_active = False
        self.external_participant.save(
            update_fields=[
                "is_active",
            ]
        )

        with self.assertRaises(
            ValidationError
        ):
            CommunicationService.send_email_message(
                conversation=self.conversation,
                author=self.author,
                body="Message externe.",
                recipients=[
                    self.external_participant,
                ],
            )