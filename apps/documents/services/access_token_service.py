

from __future__ import annotations

from django.core import signing

from apps.documents.models import DocumentVersion


class DocumentAccessTokenService:
    """
    Génère et valide les jetons temporaires donnant accès
    au contenu physique d'une version documentaire.
    """

    SALT = "easy-projet.document-version-access"
    MAX_AGE_SECONDS = 300

    @classmethod
    def create_token(
        cls,
        *,
        version: DocumentVersion,
    ) -> str:
        return signing.dumps(
            {
                "version_id": str(version.pk),
            },
            salt=cls.SALT,
            compress=True,
        )

    @classmethod
    def validate_token(
        cls,
        *,
        token: str,
        version: DocumentVersion,
    ) -> bool:
        try:
            payload = signing.loads(
                token,
                salt=cls.SALT,
                max_age=cls.MAX_AGE_SECONDS,
            )
        except (
            signing.BadSignature,
            signing.SignatureExpired,
        ):
            return False

        return (
            payload.get("version_id")
            == str(version.pk)
        )