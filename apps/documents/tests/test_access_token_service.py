

from unittest.mock import Mock, patch

from django.core import signing
from django.test import SimpleTestCase

from apps.documents.services.access_token_service import (
    DocumentAccessTokenService,
)


class DocumentAccessTokenServiceTests(SimpleTestCase):

    @staticmethod
    def make_version(version_id="version-1"):
        version = Mock()
        version.pk = version_id
        return version

    def test_created_token_is_valid(self):
        version = self.make_version()

        token = DocumentAccessTokenService.create_token(
            version=version,
        )

        self.assertTrue(
            DocumentAccessTokenService.validate_token(
                token=token,
                version=version,
            )
        )

    def test_token_is_bound_to_version(self):
        version = self.make_version("version-1")
        other_version = self.make_version("version-2")

        token = DocumentAccessTokenService.create_token(
            version=version,
        )

        self.assertFalse(
            DocumentAccessTokenService.validate_token(
                token=token,
                version=other_version,
            )
        )

    def test_invalid_token_is_rejected(self):
        version = self.make_version()

        self.assertFalse(
            DocumentAccessTokenService.validate_token(
                token="invalid-token",
                version=version,
            )
        )

    def test_expired_token_is_rejected(self):
        version = self.make_version()

        with patch(
            "apps.documents.services.access_token_service."
            "signing.loads",
            side_effect=signing.SignatureExpired("expired"),
        ):
            self.assertFalse(
                DocumentAccessTokenService.validate_token(
                    token="expired-token",
                    version=version,
                )
            )