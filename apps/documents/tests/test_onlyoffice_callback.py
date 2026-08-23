

from io import BytesIO
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from apps.documents.integrations.providers import (
    OnlyOfficeCallbackError,
    OnlyOfficeCallbackService,
)


class OnlyOfficeCallbackServiceTests(SimpleTestCase):

    def setUp(self):
        self.storage = Mock()
        self.service = OnlyOfficeCallbackService(
            storage=self.storage,
        )

        self.version = Mock()
        self.version.document = Mock()
        self.version.original_filename = "document.docx"
        self.version.mime_type = (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )

    def test_status_other_than_2_does_nothing(self):
        result = self.service.process(
            version=self.version,
            payload={
                "status": 1,
            },
        )

        self.assertIsNone(result)

    def test_status_2_requires_url(self):
        with self.assertRaises(
            OnlyOfficeCallbackError
        ):
            self.service.process(
                version=self.version,
                payload={
                    "status": 2,
                    "users": ["user-id"],
                },
            )

    def test_status_2_requires_user(self):
        with self.assertRaises(
            OnlyOfficeCallbackError
        ):
            self.service.process(
                version=self.version,
                payload={
                    "status": 2,
                    "url": (
                        "https://onlyoffice.example/"
                        "document.docx"
                    ),
                },
            )

    @patch(
        "apps.documents.integrations.providers."
        "onlyoffice_callback.User.objects.get"
    )
    @patch(
        "apps.documents.integrations.providers."
        "onlyoffice_callback."
        "OnlyOfficeDownloadService.download"
    )
    def test_status_2_creates_new_version(
        self,
        mocked_download,
        mocked_user_get,
    ):
        user = Mock()
        new_version = Mock()

        mocked_user_get.return_value = user
        mocked_download.return_value = BytesIO(
            b"Contenu modifie"
        )

        with patch.object(
            self.service.version_service,
            "create_version",
            return_value=new_version,
        ) as mocked_create_version:

            result = self.service.process(
                version=self.version,
                payload={
                    "status": 2,
                    "url": (
                        "https://onlyoffice.example/"
                        "document.docx"
                    ),
                    "users": [
                        "user-id",
                    ],
                },
            )

        self.assertIs(
            result,
            new_version,
        )

        mocked_download.assert_called_once_with(
            "https://onlyoffice.example/document.docx"
        )

        mocked_create_version.assert_called_once()

        call_kwargs = (
            mocked_create_version.call_args.kwargs
        )

        self.assertIs(
            call_kwargs["document"],
            self.version.document,
        )

        self.assertEqual(
            call_kwargs["original_filename"],
            "document.docx",
        )

        self.assertIs(
            call_kwargs["user"],
            user,
        )