from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.utils import timezone
from django.utils.html import escape

from apps.communications.models import (
    CommunicationMessage,
    CommunicationMessageRecipient,
)


class CommunicationEmailService:
    """Distribution des communications Easy Projet par email."""

    @classmethod
    def send_pending_message(cls, *, message_id) -> bool:
        message = (
            CommunicationMessage.objects
            .select_related(
                "author",
                "conversation",
                "conversation__project",
            )
            .prefetch_related(
                "attachments",
                "recipients",
                "recipients__external_participant",
            )
            .get(pk=message_id)
        )

        distributions = list(
            message.recipients.filter(
                channel=CommunicationMessageRecipient.Channel.EMAIL,
                status=CommunicationMessageRecipient.Status.PENDING,
            ).order_by("created_at")
        )

        if not distributions:
            return False

        to_addresses = cls._build_addresses(
            distributions=distributions,
            purpose=CommunicationMessageRecipient.Purpose.ACTION,
        )
        cc_addresses = cls._build_addresses(
            distributions=distributions,
            purpose=CommunicationMessageRecipient.Purpose.INFORMATION,
        )

        if not to_addresses and not cc_addresses:
            cls._mark_failed(
                distributions=distributions,
                error="Aucune adresse email de destination valide.",
            )
            return False

        email = EmailMultiAlternatives(
            subject=cls._build_subject(message=message),
            body=cls._build_body(message=message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_addresses,
            cc=cc_addresses,
        )
        email.attach_alternative(
            cls._build_html_body(message=message),
            "text/html",
        )

        if message.author and message.author.email:
            email.reply_to = [message.author.email]

        try:
            cls._attach_files(email=email, message=message)
            sent_count = email.send(fail_silently=False)

            if sent_count != 1:
                cls._mark_failed(
                    distributions=distributions,
                    error=(
                        "Le serveur de messagerie n'a pas confirmé "
                        "l'envoi."
                    ),
                )
                return False
        except Exception as error:
            cls._mark_failed(
                distributions=distributions,
                error=str(error),
            )
            return False

        cls._mark_sent(distributions=distributions)
        return True

    @staticmethod
    def _build_addresses(*, distributions, purpose: str) -> list[str]:
        addresses = []
        seen = set()

        for distribution in distributions:
            if distribution.purpose != purpose:
                continue

            email = (distribution.destination_email or "").strip().lower()

            if not email or email in seen:
                continue

            seen.add(email)
            addresses.append(email)

        return addresses

    @staticmethod
    def _build_subject(*, message: CommunicationMessage) -> str:
        project = message.conversation.project
        subject = (message.subject or "Communication projet").strip()
        return f"[{project.reference}] {subject}"

    @staticmethod
    def _build_body(*, message: CommunicationMessage) -> str:
        return (message.body or "").strip()

    @classmethod
    def _build_html_body(cls, *, message: CommunicationMessage) -> str:
        """Conserve les retours à la ligne dans les clients HTML."""

        body = escape(cls._build_body(message=message))
        return (
            '<div style="font-family: Arial, sans-serif;">'
            f"{body.replace(chr(10), '<br>')}"
            "</div>"
        )

    @staticmethod
    def _attach_files(*, email, message: CommunicationMessage) -> None:
        for attachment in message.attachments.all().order_by("created_at"):
            if not attachment.uploaded_file:
                continue

            attachment.uploaded_file.open("rb")
            try:
                content = attachment.uploaded_file.read()
            finally:
                attachment.uploaded_file.close()

            email.attach(
                filename=attachment.original_filename or "piece-jointe",
                content=content,
                mimetype=attachment.mime_type or "application/octet-stream",
            )

    @staticmethod
    @transaction.atomic
    def _mark_sent(*, distributions) -> None:
        now = timezone.now()
        distribution_ids = [distribution.pk for distribution in distributions]
        CommunicationMessageRecipient.objects.filter(
            pk__in=distribution_ids,
            status=CommunicationMessageRecipient.Status.PENDING,
        ).update(
            status=CommunicationMessageRecipient.Status.SENT,
            sent_at=now,
            error_details="",
        )

    @staticmethod
    @transaction.atomic
    def _mark_failed(*, distributions, error: str) -> None:
        max_length = (
            CommunicationMessageRecipient._meta.get_field(
                "error_details"
            ).max_length
        )
        error_details = (error or "Erreur d'envoi inconnue.")[:max_length]
        distribution_ids = [distribution.pk for distribution in distributions]
        CommunicationMessageRecipient.objects.filter(
            pk__in=distribution_ids,
        ).update(
            status=CommunicationMessageRecipient.Status.FAILED,
            error_details=error_details,
        )
