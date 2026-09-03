

from __future__ import annotations

from datetime import timedelta
from io import BytesIO
from tempfile import TemporaryDirectory

from django.test import (
    TestCase,
    override_settings,
)
from django.utils import timezone

from apps.catalogs.models import (
    CatalogType,
    CatalogValue,
)
from apps.companies.models import Company
from apps.documents.models import (
    Document,
    DocumentEditLock,
    DocumentFolder,
)
from apps.documents.services import (
    DocumentEditLockService,
    DocumentVersionService,
)
from apps.documents.storage import (
    FileSystemDocumentStorage,
)
from apps.licenses.models import ClientEnvironment
from apps.projects.models import Project
from apps.users.models import User


@override_settings(
    DOCUMENT_EDIT_LOCK_TIMEOUT_SECONDS=900,
)
class DocumentEditLockServiceTests(TestCase):
    """
    Tests des verrous applicatifs d'édition documentaire.
    """

    @classmethod
    def setUpTestData(cls):

        # --------------------------------------------------------------
        # Société
        # --------------------------------------------------------------

        cls.company = Company.objects.create(
            name="Société test verrou GED",
        )

        cls.client_environment = (
            ClientEnvironment.objects.create(
                company=cls.company,
            )
        )

        # --------------------------------------------------------------
        # Catalogues utilisateur
        # --------------------------------------------------------------

        cls.global_role_type = (
            CatalogType.objects.create(
                code="TEST_EDIT_LOCK_GLOBAL_ROLE",
                label="Rôle global test verrou",
            )
        )

        cls.access_level_type = (
            CatalogType.objects.create(
                code="TEST_EDIT_LOCK_ACCESS_LEVEL",
                label="Niveau accès test verrou",
            )
        )

        cls.global_role = (
            CatalogValue.objects.create(
                catalog_type=cls.global_role_type,
                code="USER",
                label="Utilisateur",
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

        cls.user_a = User.objects.create(
            company=cls.company,
            email="edit-lock-a@example.com",
            first_name="Alice",
            last_name="Editeur",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        cls.user_b = User.objects.create(
            company=cls.company,
            email="edit-lock-b@example.com",
            first_name="Bob",
            last_name="Concurrent",
            global_role=cls.global_role,
            access_level=cls.access_level,
        )

        # --------------------------------------------------------------
        # Statut projet
        # --------------------------------------------------------------

        cls.project_status_type = (
            CatalogType.objects.create(
                code="TEST_EDIT_LOCK_PROJECT_STATUS",
                label="Statut projet test verrou",
            )
        )

        cls.project_status = (
            CatalogValue.objects.create(
                catalog_type=cls.project_status_type,
                code="IN_PROGRESS",
                label="En cours",
                sort_order=10,
            )
        )

        # --------------------------------------------------------------
        # Projet
        # --------------------------------------------------------------

        cls.project = Project.objects.create(
            company=cls.company,
            reference="PRJ-EDIT-LOCK-001",
            name="Projet verrou GED",
            status=cls.project_status,
        )

        # --------------------------------------------------------------
        # Catalogues documentaires
        # --------------------------------------------------------------

        cls.document_type_catalog = (
            CatalogType.objects.create(
                code="TEST_EDIT_LOCK_DOCUMENT_TYPE",
                label="Type document test verrou",
            )
        )

        cls.document_status_catalog = (
            CatalogType.objects.create(
                code="TEST_EDIT_LOCK_DOCUMENT_STATUS",
                label="Statut document test verrou",
            )
        )

        cls.document_lifecycle_catalog = (
            CatalogType.objects.create(
                code="TEST_DOC_LOCK_LIFECYCLE",
                label="Cycle documentaire test verrou",
            )
        )

        cls.document_type = (
            CatalogValue.objects.create(
                catalog_type=cls.document_type_catalog,
                code="NOTE",
                label="Note technique",
                sort_order=10,
            )
        )

        cls.document_status = (
            CatalogValue.objects.create(
                catalog_type=cls.document_status_catalog,
                code="IN_PROGRESS",
                label="En cours",
                sort_order=10,
            )
        )

        cls.document_lifecycle = (
            CatalogValue.objects.create(
                catalog_type=cls.document_lifecycle_catalog,
                code="ACTIVE",
                label="Actif",
                sort_order=10,
            )
        )

        # --------------------------------------------------------------
        # Dossier
        # --------------------------------------------------------------

        cls.root_folder = (
            DocumentFolder.objects.create(
                project=cls.project,
                name="Documents",
            )
        )

    def setUp(self):

        self.temporary_directory = (
            TemporaryDirectory()
        )

        self.storage = (
            FileSystemDocumentStorage(
                self.temporary_directory.name
            )
        )

        self.version_service = (
            DocumentVersionService(
                storage=self.storage
            )
        )

        self.document = Document.objects.create(
            project=self.project,
            folder=self.root_folder,
            title="Document verrouillé",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            created_by=self.user_a,
        )

        self.version = (
            self.version_service.create_version(
                document=self.document,
                content=BytesIO(
                    b"Version 1"
                ),
                original_filename="document.docx",
                mime_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                user=self.user_a,
            )
        )

        self.document.refresh_from_db()

    def tearDown(self):

        self.temporary_directory.cleanup()

    # ------------------------------------------------------------------
    # Acquisition
    # ------------------------------------------------------------------

    def test_acquire_creates_lock_when_none_exists(
        self,
    ):
        result = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_a,
            )
        )

        self.assertTrue(
            result.acquired
        )

        self.assertTrue(
            result.is_owner
        )

        self.assertEqual(
            result.owner,
            self.user_a,
        )

        self.assertEqual(
            result.lock.document,
            self.document,
        )

        self.assertEqual(
            result.lock.version,
            self.version,
        )

        self.assertEqual(
            result.lock.user,
            self.user_a,
        )

        self.assertEqual(
            DocumentEditLock.objects.filter(
                document=self.document
            ).count(),
            1,
        )

    def test_same_user_renews_existing_lock(
        self,
    ):
        first_result = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_a,
            )
        )

        first_expiration = (
            first_result.lock.expires_at
        )

        DocumentEditLock.objects.filter(
            pk=first_result.lock.pk
        ).update(
            expires_at=(
                timezone.now()
                + timedelta(
                    seconds=60
                )
            )
        )

        second_result = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_a,
            )
        )

        self.assertTrue(
            second_result.acquired
        )

        self.assertTrue(
            second_result.is_owner
        )

        self.assertEqual(
            second_result.lock.pk,
            first_result.lock.pk,
        )

        self.assertGreater(
            second_result.lock.expires_at,
            timezone.now()
            + timedelta(
                seconds=800
            ),
        )

        self.assertEqual(
            DocumentEditLock.objects.filter(
                document=self.document
            ).count(),
            1,
        )

    def test_other_user_cannot_acquire_active_lock(
        self,
    ):
        DocumentEditLockService.acquire(
            document=self.document,
            version=self.version,
            user=self.user_a,
        )

        result = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_b,
            )
        )

        self.assertFalse(
            result.acquired
        )

        self.assertFalse(
            result.is_owner
        )

        self.assertEqual(
            result.owner,
            self.user_a,
        )

        self.assertEqual(
            result.lock.user,
            self.user_a,
        )

    def test_other_user_can_take_expired_lock(
        self,
    ):
        result_a = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_a,
            )
        )

        DocumentEditLock.objects.filter(
            pk=result_a.lock.pk
        ).update(
            expires_at=(
                timezone.now()
                - timedelta(
                    seconds=1
                )
            )
        )

        result_b = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_b,
            )
        )

        self.assertTrue(
            result_b.acquired
        )

        self.assertTrue(
            result_b.is_owner
        )

        self.assertEqual(
            result_b.owner,
            self.user_b,
        )

        self.assertEqual(
            result_b.lock.user,
            self.user_b,
        )

        self.assertEqual(
            result_b.lock.pk,
            result_a.lock.pk,
        )

    # ------------------------------------------------------------------
    # Renouvellement
    # ------------------------------------------------------------------

    def test_owner_can_refresh_lock(
        self,
    ):
        result = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_a,
            )
        )

        DocumentEditLock.objects.filter(
            pk=result.lock.pk
        ).update(
            expires_at=(
                timezone.now()
                + timedelta(
                    seconds=60
                )
            )
        )

        refreshed = (
            DocumentEditLockService.refresh(
                document=self.document,
                user=self.user_a,
            )
        )

        self.assertTrue(
            refreshed
        )

        result.lock.refresh_from_db()

        self.assertGreater(
            result.lock.expires_at,
            timezone.now()
            + timedelta(
                seconds=800
            ),
        )

    def test_other_user_cannot_refresh_lock(
        self,
    ):
        DocumentEditLockService.acquire(
            document=self.document,
            version=self.version,
            user=self.user_a,
        )

        refreshed = (
            DocumentEditLockService.refresh(
                document=self.document,
                user=self.user_b,
            )
        )

        self.assertFalse(
            refreshed
        )

    # ------------------------------------------------------------------
    # Libération
    # ------------------------------------------------------------------

    def test_owner_can_release_lock(
        self,
    ):
        DocumentEditLockService.acquire(
            document=self.document,
            version=self.version,
            user=self.user_a,
        )

        released = (
            DocumentEditLockService.release(
                document=self.document,
                user=self.user_a,
            )
        )

        self.assertTrue(
            released
        )

        self.assertFalse(
            DocumentEditLock.objects.filter(
                document=self.document
            ).exists()
        )

    def test_other_user_cannot_release_lock(
        self,
    ):
        DocumentEditLockService.acquire(
            document=self.document,
            version=self.version,
            user=self.user_a,
        )

        released = (
            DocumentEditLockService.release(
                document=self.document,
                user=self.user_b,
            )
        )

        self.assertFalse(
            released
        )

        self.assertTrue(
            DocumentEditLock.objects.filter(
                document=self.document
            ).exists()
        )

    # ------------------------------------------------------------------
    # Consultation
    # ------------------------------------------------------------------

    def test_get_active_lock_returns_active_lock(
        self,
    ):
        result = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_a,
            )
        )

        lock = (
            DocumentEditLockService.get_active_lock(
                document=self.document,
            )
        )

        self.assertIsNotNone(
            lock
        )

        self.assertEqual(
            lock.pk,
            result.lock.pk,
        )

    def test_get_active_lock_ignores_expired_lock(
        self,
    ):
        result = (
            DocumentEditLockService.acquire(
                document=self.document,
                version=self.version,
                user=self.user_a,
            )
        )

        DocumentEditLock.objects.filter(
            pk=result.lock.pk
        ).update(
            expires_at=(
                timezone.now()
                - timedelta(
                    seconds=1
                )
            )
        )

        lock = (
            DocumentEditLockService.get_active_lock(
                document=self.document,
            )
        )

        self.assertIsNone(
            lock
        )

    # ------------------------------------------------------------------
    # Cohérence document / version
    # ------------------------------------------------------------------

    def test_version_from_another_document_is_rejected(
        self,
    ):
        other_document = Document.objects.create(
            project=self.project,
            folder=self.root_folder,
            title="Autre document",
            document_type=self.document_type,
            status=self.document_status,
            lifecycle=self.document_lifecycle,
            created_by=self.user_a,
        )

        other_version = (
            self.version_service.create_version(
                document=other_document,
                content=BytesIO(
                    b"Autre version"
                ),
                original_filename="autre.docx",
                mime_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                user=self.user_a,
            )
        )

        with self.assertRaises(
            ValueError
        ):
            DocumentEditLockService.acquire(
                document=self.document,
                version=other_version,
                user=self.user_a,
            )

    def test_old_version_is_rejected(
        self,
    ):
        old_version = self.version

        new_version = (
            self.version_service.create_version(
                document=self.document,
                content=BytesIO(
                    b"Version 2"
                ),
                original_filename="document.docx",
                mime_type=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                user=self.user_a,
            )
        )

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.current_version,
            new_version,
        )

        with self.assertRaises(
            ValueError
        ):
            DocumentEditLockService.acquire(
                document=self.document,
                version=old_version,
                user=self.user_a,
            )