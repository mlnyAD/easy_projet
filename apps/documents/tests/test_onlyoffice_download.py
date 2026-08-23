

from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from django.test import SimpleTestCase

from apps.documents.integrations.providers import (
    OnlyOfficeDownloadError,
    OnlyOfficeDownloadService,
)


class OnlyOfficeDownloadServiceTests(SimpleTestCase):

    @patch(
        "apps.documents.integrations.providers."
        "onlyoffice_download.urlopen"
    )
    def test_download_returns_binary_stream(
        self,
        mocked_urlopen,
    ):
        response = MagicMock()
        response.read.return_value = b"Contenu modifie"

        context_manager = MagicMock()
        context_manager.__enter__.return_value = response

        mocked_urlopen.return_value = context_manager

        content = OnlyOfficeDownloadService.download(
            "https://onlyoffice.example/file.docx"
        )

        self.assertIsInstance(
            content,
            BytesIO,
        )

        self.assertEqual(
            content.read(),
            b"Contenu modifie",
        )

    def test_empty_url_is_rejected(self):
        with self.assertRaises(ValueError):
            OnlyOfficeDownloadService.download(
                "   "
            )

    @patch(
        "apps.documents.integrations.providers."
        "onlyoffice_download.urlopen"
    )
    def test_network_error_is_wrapped(
        self,
        mocked_urlopen,
    ):
        mocked_urlopen.side_effect = URLError(
            "Connection refused"
        )

        with self.assertRaises(
            OnlyOfficeDownloadError
        ):
            OnlyOfficeDownloadService.download(
                "https://onlyoffice.example/file.docx"
            )

    @patch(
        "apps.documents.integrations.providers."
        "onlyoffice_download.urlopen"
    )
    def test_timeout_is_configured(
        self,
        mocked_urlopen,
    ):
        response = MagicMock()
        response.read.return_value = b"data"

        context_manager = MagicMock()
        context_manager.__enter__.return_value = response

        mocked_urlopen.return_value = context_manager

        OnlyOfficeDownloadService.download(
            "https://onlyoffice.example/file.docx"
        )

        _, kwargs = mocked_urlopen.call_args

        self.assertEqual(
            kwargs["timeout"],
            OnlyOfficeDownloadService.TIMEOUT_SECONDS,
        )