from __future__ import annotations

from django.utils import timezone

from apps.notifications.models import Notification
from apps.projects.models import Project
from apps.users.models import User


class NotificationService:
    """Création et lecture des notifications personnelles."""

    @classmethod
    def upsert(
        cls,
        *,
        user: User,
        project: Project | None,
        kind: str,
        source_key: str,
        title: str,
        body: str,
        target_url: str,
    ) -> Notification:
        """Crée ou renouvelle une alerte issue du même événement."""

        notification, _created = (
            Notification.objects.update_or_create(
                user=user,
                source_key=source_key,
                defaults={
                    "project": project,
                    "kind": kind,
                    "title": title.strip(),
                    "body": body.strip(),
                    "target_url": target_url,
                    "read_at": None,
                },
            )
        )

        return notification

    @staticmethod
    def mark_as_read(
        *,
        notification: Notification,
    ) -> None:
        if notification.read_at is not None:
            return

        notification.read_at = timezone.now()
        notification.save(
            update_fields=("read_at", "updated_at"),
        )
