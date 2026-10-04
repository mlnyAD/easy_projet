

from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from apps.documents.integrations.credentials import (
    IntegrationCredentialResolver,
)
from apps.documents.integrations.signature import (
    SignatureDocumentSubmission,
    SignatureIntegration,
    SignatureRecipientSubmission,
    SignatureSubmission,
)
from apps.documents.models import SignatureRequest
from apps.integrations.models import ExternalIntegration


class DocumensoIntegrationError(RuntimeError):
    """
    Erreur fonctionnelle lors d'un appel à Documenso.
    """


class DocumensoAdapter(SignatureIntegration):
    """
    Adaptateur Documenso API V2.

    Chaque demande Easy Projet devient une enveloppe Documenso contenant
    un ou plusieurs PDF. Les champs Signature et Date sont positionnés
    automatiquement sur la dernière page de chaque PDF.
    """

    provider_code = "DOCUMENSO"

    DEFAULT_BASE_URL = "https://app.documenso.com/api/v2"
    REQUEST_TIMEOUT_SECONDS = 30

    FIELD_POSITION_X = 10
    FIELD_POSITION_Y = 80
    FIELD_WIDTH = 30
    FIELD_HEIGHT = 5
    DATE_POSITION_X = 50
    DATE_WIDTH = 20
    DATE_HEIGHT = 3
    RECIPIENT_VERTICAL_OFFSET = 10
    MINIMUM_POSITION_Y = 5

    def __init__(
        self,
        *,
        credential_resolver: (
            IntegrationCredentialResolver | None
        ) = None,
    ) -> None:
        self.credential_resolver = (
            credential_resolver
            or IntegrationCredentialResolver()
        )

    def create_signature_request(
        self,
        *,
        external_integration: ExternalIntegration,
        signature_request: SignatureRequest,
        documents: tuple[SignatureDocumentSubmission, ...],
        recipients: tuple[SignatureRecipientSubmission, ...],
    ) -> SignatureSubmission:
        """
        Crée l'enveloppe puis la distribue aux signataires.
        """

        if not documents:
            raise ValueError(
                "La demande de signature ne contient aucun document."
            )

        if not recipients:
            raise ValueError(
                "La demande de signature ne contient aucun signataire."
            )

        api_key = self.credential_resolver.resolve(
            external_integration.credential_reference
        )

        base_url = self._get_base_url(
            external_integration
        )

        payload = self._build_create_payload(
            signature_request=signature_request,
            documents=documents,
            recipients=recipients,
        )

        response = self._post_multipart(
            url=f"{base_url}/envelope/create",
            api_key=api_key,
            payload=payload,
            documents=documents,
        )

        provider_request_id = self._get_required_string(
            response,
            "id",
            "Documenso n'a retourné aucun identifiant d'enveloppe.",
        )

        self._post_json(
            url=f"{base_url}/envelope/distribute",
            api_key=api_key,
            payload={
                "envelopeId": provider_request_id,
            },
        )

        return SignatureSubmission(
            provider_request_id=provider_request_id,
        )

    def cancel_signature_request(
        self,
        *,
        external_integration: ExternalIntegration,
        signature_request: SignatureRequest,
    ) -> None:
        """
        Annule une enveloppe Documenso encore active.
        """

        provider_request_id = (
            signature_request.provider_request_id.strip()
        )

        if not provider_request_id:
            raise ValueError(
                "La demande ne possède pas d'identifiant Documenso."
            )

        api_key = self.credential_resolver.resolve(
            external_integration.credential_reference
        )

        base_url = self._get_base_url(
            external_integration
        )

        self._post_json(
            url=f"{base_url}/envelope/cancel",
            api_key=api_key,
            payload={
                "envelopeId": provider_request_id,
            },
        )

    def verify_webhook(
        self,
        *,
        external_integration: ExternalIntegration,
        headers: dict[str, str],
        body: bytes,
    ) -> bool:
        """
        Vérifie le header X-Documenso-Secret.

        Documenso transmet le secret configuré en clair dans ce header ;
        la comparaison doit donc être effectuée en temps constant.
        """

        del body

        configuration = external_integration.configuration

        secret_reference = configuration.get(
            "webhook_secret_reference",
            "",
        )

        if not isinstance(secret_reference, str):
            return False

        secret_reference = secret_reference.strip()

        if not secret_reference:
            return False

        try:
            expected_secret = self.credential_resolver.resolve(
                secret_reference
            )
        except ValueError:
            return False

        normalized_headers = {
            key.lower(): value
            for key, value in headers.items()
        }

        received_secret = normalized_headers.get(
            "x-documenso-secret",
            "",
        )

        return secrets.compare_digest(
            received_secret,
            expected_secret,
        )

    def _build_create_payload(
        self,
        *,
        signature_request: SignatureRequest,
        documents: tuple[SignatureDocumentSubmission, ...],
        recipients: tuple[SignatureRecipientSubmission, ...],
    ) -> dict[str, Any]:
        sequential = len(
            {
                recipient.signing_order
                for recipient in recipients
            }
        ) > 1

        return {
            "type": "DOCUMENT",
            "title": signature_request.title,
            "externalId": str(signature_request.pk),
            "recipients": [
                {
                    "email": recipient.email,
                    "name": recipient.full_name,
                    "role": "SIGNER",
                    "signingOrder": recipient.signing_order,
                    "fields": self._build_recipient_fields(
                        recipient_index=recipient_index,
                        documents=documents,
                    ),
                }
                for recipient_index, recipient in enumerate(
                    recipients
                )
            ],
            "meta": {
                "subject": (
                    f"Signature demandée : "
                    f"{signature_request.title}"
                ),
                "message": (
                    "Veuillez consulter et signer les documents "
                    "transmis."
                ),
                "signingOrder": (
                    "SEQUENTIAL"
                    if sequential
                    else "PARALLEL"
                ),
            },
        }

    def _build_recipient_fields(
        self,
        *,
        recipient_index: int,
        documents: tuple[SignatureDocumentSubmission, ...],
    ) -> list[dict[str, int | str]]:
        position_y = (
            self.FIELD_POSITION_Y
            - (
                recipient_index
                * self.RECIPIENT_VERTICAL_OFFSET
            )
        )

        if position_y < self.MINIMUM_POSITION_Y:
            raise ValueError(
                "Le positionnement automatique ne permet pas "
                "d'ajouter autant de signataires. Réduisez le nombre "
                "de signataires ou utilisez ultérieurement le "
                "positionnement manuel."
            )

        fields: list[dict[str, int | str]] = []

        for document_index, document in enumerate(documents):
            page_number = self._get_page_count(
                document.content
            )

            fields.extend(
                [
                    {
                        "identifier": document_index,
                        "type": "SIGNATURE",
                        "page": page_number,
                        "positionX": self.FIELD_POSITION_X,
                        "positionY": position_y,
                        "width": self.FIELD_WIDTH,
                        "height": self.FIELD_HEIGHT,
                    },
                    {
                        "identifier": document_index,
                        "type": "DATE",
                        "page": page_number,
                        "positionX": self.DATE_POSITION_X,
                        "positionY": position_y,
                        "width": self.DATE_WIDTH,
                        "height": self.DATE_HEIGHT,
                    },
                ]
            )

        return fields

    @staticmethod
    def _get_page_count(
        content,
    ) -> int:
        try:
            content.seek(0)

            reader = PdfReader(content)

            page_count = len(reader.pages)

            content.seek(0)
        except (
            OSError,
            PdfReadError,
        ) as exc:
            raise ValueError(
                "Impossible de lire le PDF à signer."
            ) from exc

        if page_count < 1:
            raise ValueError(
                "Le PDF à signer ne contient aucune page."
            )

        return page_count

    @classmethod
    def _get_base_url(
        cls,
        external_integration: ExternalIntegration,
    ) -> str:
        configuration = external_integration.configuration

        base_url = configuration.get(
            "base_url",
            cls.DEFAULT_BASE_URL,
        )

        if not isinstance(base_url, str):
            raise ValueError(
                "La configuration base_url de Documenso est invalide."
            )

        normalized_url = base_url.strip().rstrip("/")

        if not normalized_url.startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "La configuration base_url de Documenso "
                "doit être une URL HTTP(S)."
            )

        return normalized_url

    def _post_json(
        self,
        *,
        url: str,
        api_key: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")

        request = Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        return self._execute_request(request)

    def _post_multipart(
        self,
        *,
        url: str,
        api_key: str,
        payload: dict[str, Any],
        documents: tuple[SignatureDocumentSubmission, ...],
    ) -> dict[str, Any]:
        boundary = (
            f"----EasyProjet{uuid4().hex}"
        )

        body = self._build_multipart_body(
            boundary=boundary,
            payload=payload,
            documents=documents,
        )

        request = Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": api_key,
                "Content-Type": (
                    f"multipart/form-data; boundary={boundary}"
                ),
                "Accept": "application/json",
            },
        )

        return self._execute_request(request)

    def _build_multipart_body(
        self,
        *,
        boundary: str,
        payload: dict[str, Any],
        documents: tuple[SignatureDocumentSubmission, ...],
    ) -> bytes:
        parts: list[bytes] = []
        delimiter = f"--{boundary}\r\n".encode()

        parts.extend(
            [
                delimiter,
                (
                    b'Content-Disposition: form-data; '
                    b'name="payload"\r\n'
                ),
                b"Content-Type: application/json\r\n\r\n",
                json.dumps(payload).encode("utf-8"),
                b"\r\n",
            ]
        )

        for document in documents:
            filename = Path(document.filename).name

            if not filename:
                raise ValueError(
                    "Le nom du PDF envoyé à Documenso est invalide."
                )

            try:
                document.content.seek(0)
                content = document.content.read()
                document.content.seek(0)
            except OSError as exc:
                raise ValueError(
                    "Impossible de lire le PDF à envoyer "
                    "à Documenso."
                ) from exc

            if not isinstance(content, bytes) or not content:
                raise ValueError(
                    "Le PDF envoyé à Documenso est vide."
                )

            parts.extend(
                [
                    delimiter,
                    (
                        b'Content-Disposition: form-data; '
                        b'name="files"; '
                        + (
                            f'filename="{filename}"\r\n'
                        ).encode("utf-8")
                    ),
                    b"Content-Type: application/pdf\r\n\r\n",
                    content,
                    b"\r\n",
                ]
            )

        parts.extend(
            [
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )

        return b"".join(parts)

    def _execute_request(
        self,
        request: Request,
    ) -> dict[str, Any]:
        try:
            with urlopen(
                request,
                timeout=self.REQUEST_TIMEOUT_SECONDS,
            ) as response:
                content = response.read()

        except HTTPError as exc:
            raise DocumensoIntegrationError(
                self._get_http_error_message(exc)
            ) from exc
        except (
            URLError,
            TimeoutError,
            OSError,
        ) as exc:
            raise DocumensoIntegrationError(
                "Impossible de joindre Documenso."
            ) from exc

        try:
            data = json.loads(
                content.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise DocumensoIntegrationError(
                "Documenso a retourné une réponse invalide."
            ) from exc

        if not isinstance(data, dict):
            raise DocumensoIntegrationError(
                "Documenso a retourné une réponse invalide."
            )

        return data

    @staticmethod
    def _get_required_string(
        data: dict[str, Any],
        key: str,
        message: str,
    ) -> str:
        value = data.get(key)

        if not isinstance(value, str) or not value.strip():
            raise DocumensoIntegrationError(message)

        return value.strip()

    @staticmethod
    def _get_http_error_message(
        error: HTTPError,
    ) -> str:
        try:
            content = error.read().decode("utf-8")
            data = json.loads(content)
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            return (
                "Documenso a refusé la demande "
                f"(HTTP {error.code})."
            )

        if not isinstance(data, dict):
            return (
                "Documenso a refusé la demande "
                f"(HTTP {error.code})."
            )

        message = (
            data.get("error")
            or data.get("message")
        )

        if isinstance(message, str) and message.strip():
            return (
                "Documenso a refusé la demande : "
                f"{message.strip()}"
            )

        return (
            "Documenso a refusé la demande "
            f"(HTTP {error.code})."
        )