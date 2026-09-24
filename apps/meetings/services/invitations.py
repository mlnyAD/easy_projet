from __future__ import annotations

from dataclasses import dataclass

from django.utils import timezone

from apps.communications.email_service import CommunicationEmailService
from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessageRecipient,
)
from apps.communications.services import CommunicationService
from apps.meetings.models import Meeting


class MeetingInvitationError(Exception):
    """Erreur empêchant l'envoi des invitations d'une réunion."""


@dataclass(frozen=True)
class MeetingInvitationResult:
    """Résultat de la diffusion d'une invitation."""

    email_failed: bool


class MeetingInvitationService:
    """Diffuse une convocation enregistrée, à la demande du rédacteur."""

    CONVERSATION_TITLE = "Réunions"

    @classmethod
    def send(
        cls,
        *,
        meeting: Meeting,
        author,
    ) -> MeetingInvitationResult:
        meeting = (
            Meeting.objects
            .select_related("project", "organizer")
            .prefetch_related("participants__participant")
            .get(pk=meeting.pk)
        )

        internal_recipients = []
        direct_email_recipients = []

        for participant in meeting.participants.filter(is_active=True):
            if participant.participant_id is not None:
                internal_recipients.append(participant.participant)
                continue

            if participant.external_email:
                direct_email_recipients.append(
                    participant.external_email
                )

        if not internal_recipients and not direct_email_recipients:
            raise MeetingInvitationError(
                "La réunion ne possède aucun participant à inviter."
            )

        conversation, _created = (
            CommunicationConversation.objects.get_or_create(
                project=meeting.project,
                title=cls.CONVERSATION_TITLE,
                is_active=True,
                defaults={"created_by": author},
            )
        )

        message = CommunicationService.send_project_message(
            conversation=conversation,
            author=author,
            subject=(
                f"Invitation — {meeting.reference} — {meeting.subject}"
            ),
            body=cls._build_body(meeting=meeting),
            internal_recipients=internal_recipients,
            direct_email_recipients=direct_email_recipients,
            recipient_purposes={
                email.strip().lower(): (
                    CommunicationMessageRecipient.Purpose.ACTION
                )
                for email in direct_email_recipients
            },
        )

        email_failed = False

        if direct_email_recipients:
            email_failed = not (
                CommunicationEmailService.send_pending_message(
                    message_id=message.pk,
                )
            )

        if not email_failed:
            meeting.invitations_sent_at = timezone.now()
            meeting.save(
                update_fields=[
                    "invitations_sent_at",
                    "updated_at",
                ]
            )

        return MeetingInvitationResult(
            email_failed=email_failed,
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
