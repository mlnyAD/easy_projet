

from unittest.mock import Mock
from uuid import uuid4
from django.test import SimpleTestCase, override_settings

from apps.documents.integrations import DocumentCapability
from apps.documents.integrations.providers import OnlyOfficeAdapter


class OnlyOfficeAdapterTests(SimpleTestCase):

    def setUp(self):
        self.adapter = OnlyOfficeAdapter()

    @staticmethod
    def make_version(
        *,
        mime_type: str,
        filename: str = "document.docx",
    ):
        version = Mock()

        version.pk = uuid4()
        version.document_id = uuid4()
        version.mime_type = mime_type
        version.original_filename = filename

        return version

    # ------------------------------------------------------------------
    # Formats supportés
    # ------------------------------------------------------------------

    def test_supports_docx_for_edit(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        self.assertTrue(
            self.adapter.supports(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
            )
        )

    def test_supports_xlsx_for_edit(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            filename="classeur.xlsx",
        )

        self.assertTrue(
            self.adapter.supports(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
            )
        )

    def test_supports_pptx_for_edit(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
            filename="presentation.pptx",
        )

        self.assertTrue(
            self.adapter.supports(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
            )
        )

    def test_supports_office_view(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        self.assertTrue(
            self.adapter.supports(
                version=version,
                capability=DocumentCapability.OFFICE_VIEW,
            )
        )

    # ------------------------------------------------------------------
    # Formats / capacités refusés
    # ------------------------------------------------------------------

    def test_rejects_pdf(self):
        version = self.make_version(
            mime_type="application/pdf",
            filename="document.pdf",
        )

        self.assertFalse(
            self.adapter.supports(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
            )
        )

    def test_rejects_cad_capability(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        self.assertFalse(
            self.adapter.supports(
                version=version,
                capability=DocumentCapability.CAD_VIEW,
            )
        )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @override_settings(
        ONLYOFFICE_URL="",
        ONLYOFFICE_JWT_SECRET="secret",
    )
    def test_open_rejects_missing_server_url(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        with self.assertRaises(RuntimeError):
            self.adapter.open(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
                user=Mock(),
            )

    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET="",
    )
    def test_open_rejects_missing_jwt_secret(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        with self.assertRaises(RuntimeError):
            self.adapter.open(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
                user=Mock(),
            )

    # ------------------------------------------------------------------
    # Données retournées
    # ------------------------------------------------------------------

    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com/",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_open_normalizes_server_url(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=Mock(),
        )

        self.assertEqual(
            result["server_url"],
            "https://onlyoffice.example.com",
        )

    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_open_returns_expected_payload(self):
        mime_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

        version = self.make_version(
            mime_type=mime_type,
            filename="compte_rendu.docx",
        )

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=Mock(),
        )

        self.assertEqual(
            result["provider"],
            "ONLYOFFICE",
        )

        self.assertEqual(
            result["server_url"],
            "https://onlyoffice.example.com",
        )

        self.assertEqual(
            result["version_id"],
            str(version.pk),
        )

        self.assertEqual(
            result["document_id"],
            str(version.document_id),
        )

        self.assertEqual(
            result["filename"],
            "compte_rendu.docx",
        )

        self.assertEqual(
            result["mime_type"],
            mime_type,
        )

        self.assertEqual(
            result["capability"],
            DocumentCapability.OFFICE_EDIT,
        )

    # ------------------------------------------------------------------
    # Sécurité d'utilisation
    # ------------------------------------------------------------------

    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET="secret",
    )
    def test_open_rejects_unsupported_document(self):
        version = self.make_version(
            mime_type="application/pdf",
            filename="document.pdf",
        )

        with self.assertRaises(ValueError):
            self.adapter.open(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
                user=Mock(),
            )
            
    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_docx_builds_word_editor_config(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            filename="document.docx",
        )

        user = Mock()
        user.pk = uuid4()
        user.__str__ = Mock(return_value="Jean Dupont")

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=user,
        )

        config = result["config"]

        self.assertEqual(
            config["documentType"],
            "word",
        )

        self.assertEqual(
            config["document"]["fileType"],
            "docx",
        )

        self.assertEqual(
            config["document"]["key"],
            str(version.pk),
        )

        self.assertEqual(
            config["document"]["title"],
            "document.docx",
        )

        self.assertEqual(
            config["editorConfig"]["mode"],
            "edit",
        )

        self.assertEqual(
            config["editorConfig"]["user"]["id"],
            str(user.pk),
        )

        self.assertEqual(
            config["editorConfig"]["user"]["name"],
            "Jean Dupont",
        )


    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_xlsx_builds_cell_editor_config(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            filename="classeur.xlsx",
        )

        user = Mock()
        user.pk = uuid4()

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=user,
        )

        config = result["config"]

        self.assertEqual(
            config["documentType"],
            "cell",
        )

        self.assertEqual(
            config["document"]["fileType"],
            "xlsx",
        )


    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_pptx_builds_slide_editor_config(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
            filename="presentation.pptx",
        )

        user = Mock()
        user.pk = uuid4()

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=user,
        )

        config = result["config"]

        self.assertEqual(
            config["documentType"],
            "slide",
        )

        self.assertEqual(
            config["document"]["fileType"],
            "pptx",
        )


    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_office_view_builds_view_mode(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            filename="document.docx",
        )

        user = Mock()
        user.pk = uuid4()

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_VIEW,
            user=user,
        )

        self.assertEqual(
            result["config"]["editorConfig"]["mode"],
            "view",
        )


    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_config_contains_content_and_callback_urls(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            filename="document.docx",
        )

        user = Mock()
        user.pk = uuid4()

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=user,
        )

        config = result["config"]

        document_url = config["document"]["url"]
        callback_url = config["editorConfig"]["callbackUrl"]

        self.assertTrue(
            document_url.startswith(
                "https://easy-projet.example.com/"
            )
        )

        self.assertIn(
            f"/documents/versions/{version.pk}/content/",
            document_url,
        )

        self.assertIn(
            "?token=",
            document_url,
        )

        self.assertEqual(
            callback_url,
            (
                "https://easy-projet.example.com/"
                f"documents/versions/{version.pk}/callback/"
            ),
        )


    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_api_url_points_to_onlyoffice_api_script(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )

        user = Mock()
        user.pk = uuid4()

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=user,
        )

        self.assertEqual(
            result["api_url"],
            (
                "https://onlyoffice.example.com/"
                "web-apps/apps/api/documents/api.js"
            ),
        )


    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL=(
            "https://easy-projet.example.com"
        ),
    )
    def test_config_contains_valid_jwt(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            filename="document.docx",
        )

        user = Mock()
        user.pk = uuid4()

        result = self.adapter.open(
            version=version,
            capability=DocumentCapability.OFFICE_EDIT,
            user=user,
        )

        config = result["config"]
        token = config["token"]

        from apps.documents.integrations.providers import (
            OnlyOfficeJwtService,
        )

        decoded = OnlyOfficeJwtService.decode(
            token
        )

        expected = dict(config)
        expected.pop("token")

        self.assertEqual(
            decoded,
            expected,
        )
        
    @override_settings(
        ONLYOFFICE_URL="https://onlyoffice.example.com",
        ONLYOFFICE_JWT_SECRET=(
            "easy-projet-onlyoffice-test-secret-32chars"
        ),
        EASY_PROJET_PUBLIC_URL="",
    )
    def test_open_rejects_missing_easy_projet_public_url(self):
        version = self.make_version(
            mime_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            )
        )

        with self.assertRaises(RuntimeError):
            self.adapter.open(
                version=version,
                capability=DocumentCapability.OFFICE_EDIT,
                user=Mock(),
            )