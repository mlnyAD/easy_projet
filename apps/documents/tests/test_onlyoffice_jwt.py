

import jwt

from django.test import SimpleTestCase, override_settings

from apps.documents.integrations.providers import (
    OnlyOfficeJwtService,
)

TEST_JWT_SECRET = (
    "easy-projet-onlyoffice-test-secret-32chars"
)

class OnlyOfficeJwtServiceTests(SimpleTestCase):

    @override_settings(
        ONLYOFFICE_JWT_SECRET=TEST_JWT_SECRET,
    )
    def test_encode_and_decode(self):
        payload = {
            "document": {
                "key": "version-1",
            },
        }

        token = OnlyOfficeJwtService.encode(
            payload
        )

        decoded = OnlyOfficeJwtService.decode(
            token
        )

        self.assertEqual(
            decoded,
            payload,
        )

    @override_settings(
        ONLYOFFICE_JWT_SECRET=TEST_JWT_SECRET,
    )
    def test_token_is_hs256(self):
        token = OnlyOfficeJwtService.encode(
            {
                "test": "value",
            }
        )

        header = jwt.get_unverified_header(
            token
        )

        self.assertEqual(
            header["alg"],
            "HS256",
        )

    @override_settings(
        ONLYOFFICE_JWT_SECRET="",
    )
    def test_missing_secret_is_rejected(self):
        with self.assertRaises(RuntimeError):
            OnlyOfficeJwtService.encode(
                {
                    "test": "value",
                }
            )

    @override_settings(
        ONLYOFFICE_JWT_SECRET=TEST_JWT_SECRET,
    )
    def test_invalid_signature_is_rejected(self):
        token = jwt.encode(
            {
                "test": "value",
            },
            "another-wrong-secret-with-32-characters",
            algorithm="HS256",
        )

        with self.assertRaises(
            jwt.InvalidSignatureError
        ):
            OnlyOfficeJwtService.decode(
                token
            )

    @override_settings(
        ONLYOFFICE_JWT_SECRET=TEST_JWT_SECRET,
    )
    def test_empty_token_is_rejected(self):
        with self.assertRaises(ValueError):
            OnlyOfficeJwtService.decode(
                ""
            )

    @override_settings(
        ONLYOFFICE_JWT_SECRET=TEST_JWT_SECRET,
    )
    def test_try_decode_returns_payload(self):
        token = OnlyOfficeJwtService.encode(
            {
                "status": 2,
            }
        )

        payload = OnlyOfficeJwtService.try_decode(
            token
        )

        self.assertEqual(
            payload,
            {
                "status": 2,
            },
        )

    @override_settings(
        ONLYOFFICE_JWT_SECRET=TEST_JWT_SECRET,
    )
    def test_try_decode_invalid_token_returns_none(self):
        self.assertIsNone(
            OnlyOfficeJwtService.try_decode(
                "invalid-token"
            )
        )