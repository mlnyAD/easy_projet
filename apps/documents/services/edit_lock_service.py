

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.documents.models import (
    Document,
    DocumentEditLock,
    DocumentVersion,
)
from apps.users.models import User


@dataclass(frozen=True)
class DocumentEditLockResult:
    acquired: bool
    lock: DocumentEditLock
    owner: User
    is_owner: bool


class DocumentEditLockService:
    """
    Gestion des verrous applicatifs d'édition documentaire.

    Responsabilités :
    - acquérir un verrou ;
    - renouveler un verrou détenu par le même utilisateur ;
    - reprendre un verrou expiré ;
    - refuser l'édition si un autre utilisateur détient
      encore un verrou valide ;
    - libérer un verrou.
    """

    @staticmethod
    def _get_timeout_seconds() -> int:
        timeout = getattr(
            settings,
            "DOCUMENT_EDIT_LOCK_TIMEOUT_SECONDS",
            900,
        )

        timeout = int(timeout)

        if timeout <= 0:
            raise ValueError(
                "DOCUMENT_EDIT_LOCK_TIMEOUT_SECONDS "
                "doit être strictement positif."
            )

        return timeout

    @classmethod
    def _get_expiration(cls):
        return (
            timezone.now()
            + timezone.timedelta(
                seconds=cls._get_timeout_seconds()
            )
        )

    @classmethod
    @transaction.atomic
    def acquire(
        cls,
        *,
        document: Document,
        version: DocumentVersion,
        user: User,
    ) -> DocumentEditLockResult:
        """
        Tente d'acquérir le verrou du document.

        Cas possibles :
        - aucun verrou : création ;
        - verrou du même utilisateur : renouvellement ;
        - verrou expiré : reprise ;
        - verrou valide d'un autre utilisateur : refus.
        """

        locked_document = (
            Document.objects
            .select_for_update()
            .get(pk=document.pk)
        )

        if version.document_id != locked_document.pk:
            raise ValueError(
                "La version doit appartenir au document."
            )

        if (
            locked_document.current_version_id
            != version.pk
        ):
            raise ValueError(
                "Seule la version courante peut être "
                "ouverte en édition."
            )

        now = timezone.now()
        expires_at = cls._get_expiration()

        try:
            lock = (
                DocumentEditLock.objects
                .select_related(
                    "user",
                    "version",
                )
                .get(
                    document=locked_document
                )
            )

        except DocumentEditLock.DoesNotExist:
            lock = DocumentEditLock.objects.create(
                document=locked_document,
                version=version,
                user=user,
                expires_at=expires_at,
            )

            return DocumentEditLockResult(
                acquired=True,
                lock=lock,
                owner=user,
                is_owner=True,
            )

        if lock.user_id == user.pk:
            lock.version = version
            lock.expires_at = expires_at

            lock.save(
                update_fields=[
                    "version",
                    "expires_at",
                    "updated_at",
                ]
            )

            return DocumentEditLockResult(
                acquired=True,
                lock=lock,
                owner=user,
                is_owner=True,
            )

        if lock.expires_at <= now:
            lock.version = version
            lock.user = user
            lock.expires_at = expires_at

            lock.save(
                update_fields=[
                    "version",
                    "user",
                    "expires_at",
                    "updated_at",
                ]
            )

            return DocumentEditLockResult(
                acquired=True,
                lock=lock,
                owner=user,
                is_owner=True,
            )

        return DocumentEditLockResult(
            acquired=False,
            lock=lock,
            owner=lock.user,
            is_owner=False,
        )

    @classmethod
    @transaction.atomic
    def refresh(
        cls,
        *,
        document: Document,
        user: User,
    ) -> bool:
        """
        Renouvelle le verrou si l'utilisateur
        en est toujours propriétaire.
        """

        lock = (
            DocumentEditLock.objects
            .select_for_update()
            .filter(
                document=document,
            )
            .first()
        )

        if lock is None:
            return False

        if lock.user_id != user.pk:
            return False

        lock.expires_at = (
            cls._get_expiration()
        )

        lock.save(
            update_fields=[
                "expires_at",
                "updated_at",
            ]
        )

        return True

    @staticmethod
    @transaction.atomic
    def release(
        *,
        document: Document,
        user: User,
    ) -> bool:
        """
        Libère le verrou uniquement si l'utilisateur
        en est propriétaire.
        """

        lock = (
            DocumentEditLock.objects
            .select_for_update()
            .filter(
                document=document,
            )
            .first()
        )

        if lock is None:
            return False

        if lock.user_id != user.pk:
            return False

        lock.delete()

        return True

    @staticmethod
    def get_active_lock(
        *,
        document: Document,
    ) -> DocumentEditLock | None:
        """
        Retourne le verrou actif du document.

        Un verrou expiré est considéré comme inexistant.
        """

        lock = (
            DocumentEditLock.objects
            .select_related(
                "user",
                "version",
            )
            .filter(
                document=document,
            )
            .first()
        )

        if lock is None:
            return None

        if lock.expires_at <= timezone.now():
            return None

        return lock