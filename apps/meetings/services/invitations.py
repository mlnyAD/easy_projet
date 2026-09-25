from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape, linebreaks

from apps.meetings.models import Meeting
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


class MeetingInvitationError(Exception):
    """Erreur empêchant l'envoi des invitations d'une réunion."""


@dataclass(frozen=True)
class MeetingInvitationResult:
    """Résultat de la diffusion d'une invitation."""

    email_failed: bool


class MeetingInvitationService:
    """Diffuse les invitations internes et externes d'une réunion."""

    @classmethod
    def send(
        cls,
        *,
        meeting: Meeting,
        author,
    ) -> MeetingInvitationResult:
        meeting = (
            Meeting.objects.select_related("project", "organizer")
            .prefetch_related("participants__participant")
            .get(pk=meeting.pk)
        )

        internal_recipients = []
        external_email_recipients = []

        for participant in meeting.participants.filter(is_active=True):
            if participant.participant_id is not None:
                internal_recipients.append(participant.participant)
                continue

            if participant.external_email:
                external_email_recipients.append(
                    participant.external_email
                )

        if (
            not internal_recipients
            and not external_email_recipients
        ):
            raise MeetingInvitationError(
                "La réunion ne possède aucun participant à inviter."
            )

        cls._create_internal_notifications(
            meeting=meeting,
            recipients=internal_recipients,
        )

        email_failed = not cls._send_external_emails(
            meeting=meeting,
            author=author,
            recipients=external_email_recipients,
        )

        if not email_failed:
            meeting.invitations_sent_at = timezone.now()
            meeting.save(
                update_fields=(
                    "invitations_sent_at",
                    "updated_at",
                ),
            )

        return MeetingInvitationResult(
            email_failed=email_failed,
        )

    @classmethod
    def _create_internal_notifications(
        cls,
        *,
        meeting: Meeting,
        recipients: list,
    ) -> None:
        target_url = reverse(
            "meetings:update",
            kwargs={"pk": meeting.pk},
        )
        source_key = f"meeting-invitation:{meeting.pk}"
        title = f"Invitation — {meeting.subject}"
        body = cls._build_notification_body(meeting=meeting)

        for recipient in recipients:
            NotificationService.upsert(
                user=recipient,
                project=meeting.project,
                kind=Notification.Kind.MEETING_INVITATION,
                source_key=source_key,
                title=title,
                body=body,
                target_url=target_url,
            )

    @classmethod
    def _send_external_emails(
        cls,
        *,
        meeting: Meeting,
        author,
        recipients: list[str],
    ) -> bool:
        """Envoie l'invitation aux personnes sans compte Easy Projet."""

        addresses = cls._deduplicate_addresses(recipients=recipients)

        if not addresses:
            return True

        body = cls._build_body(meeting=meeting)
        email = EmailMultiAlternatives(
            subject=(
                f"[{meeting.project.reference}] Invitation "
                f"— {meeting.reference} — {meeting.subject}"
            ),
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=addresses,
        )

        if author.email:
            email.reply_to = [author.email]

        email.attach_alternative(
            str(linebreaks(escape(body))),
            "text/html",
        )

        try:
            return email.send(fail_silently=False) == 1
        except Exception:
            return False

    @staticmethod
    def _deduplicate_addresses(*, recipients: list[str]) -> list[str]:
        addresses = []
        seen = set()

        for recipient in recipients:
            address = recipient.strip().lower()

            if not address or address in seen:
                continue

            seen.add(address)
            addresses.append(address)

        return addresses

    @staticmethod
    def _build_notification_body(*, meeting: Meeting) -> str:
        scheduled_at = timezone.localtime(meeting.scheduled_at)

        return (
            f"{meeting.project.reference} — "
            f"{scheduled_at:%d/%m/%Y à %H:%M}"
        )

    @staticmethod
    def _build_body(*, meeting: Meeting) -> str:
        scheduled_at = timezone.localtime(meeting.scheduled_at)

        lines = [
            "Vous êtes invité(e) à la réunion suivante.",
            "",
            f"Projet : {meeting.project.reference} — {meeting.project.name}",
            f"Réunion : {meeting.subject}",
            (
                "Date et heure : "
                f"{scheduled_at:%d/%m/%Y à %H:%M}"
            ),
        ]

        if meeting.duration_hours is not None:
            lines.append(
                f"Durée prévue : {meeting.duration_hours} h"
            )

        if meeting.location:
            lines.append(f"Lieu : {meeting.location}")

        if meeting.agenda:
            lines.extend(["", "Ordre du jour :", meeting.agenda])

        if meeting.notes:
            lines.extend(["", "Informations :", meeting.notes])

        return "\n".join(lines)
