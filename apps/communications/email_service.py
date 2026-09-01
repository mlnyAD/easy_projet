

from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from apps.communications.models import (
    CommunicationMessage,
    CommunicationMessageRecipient,
)


class CommunicationEmailService:
    """
    Distribution email des communications Easy Projet.

    Un message Easy Projet donne lieu à un email groupé :

    - les destinataires "Pour action" sont placés en To ;
    - les destinataires "Pour information" sont placés en Cc.

    Le service traite uniquement les distributions EMAIL
    encore à l'état PENDING.
    """

    @classmethod
    def send_pending_message(
        cls,
        *,
        message_id,
    ) -> bool:
        """
        Distribue les destinataires EMAIL en attente
        d'une communication.

        Retourne True si l'envoi a été effectué avec succès.

        Retourne False lorsqu'il n'existe rien à envoyer
        ou lorsque l'envoi échoue.
        """

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
            .get(
                pk=message_id,
            )
        )

        distributions = list(
            message.recipients
            .filter(
                channel=(
                    CommunicationMessageRecipient
                    .Channel
                    .EMAIL
                ),
                status=(
                    CommunicationMessageRecipient
                    .Status
                    .PENDING
                ),
            )
            .order_by(
                "created_at",
            )
        )

        if not distributions:
            return False

        to_addresses = cls._build_addresses(
            distributions=distributions,
            purpose=(
                CommunicationMessageRecipient
                .Purpose
                .ACTION
            ),
        )

        cc_addresses = cls._build_addresses(
            distributions=distributions,
            purpose=(
                CommunicationMessageRecipient
                .Purpose
                .INFORMATION
            ),
        )

        if (
            not to_addresses
            and not cc_addresses
        ):
            cls._mark_failed(
                distributions=distributions,
                error=(
                    "Aucune adresse email "
                    "de destination valide."
                ),
            )

            return False

        email = EmailMessage(
            subject=cls._build_subject(
                message=message,
            ),
            body=cls._build_body(
                message=message,
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_addresses,
            cc=cc_addresses,
        )

        if (
            message.author
            and message.author.email
        ):
            email.reply_to = [
                message.author.email,
            ]

        try:
            cls._attach_files(
                email=email,
                message=message,
            )

            sent_count = email.send(
                fail_silently=False,
            )

            if sent_count != 1:
                cls._mark_failed(
                    distributions=distributions,
                    error=(
                        "Le serveur de messagerie "
                        "n'a pas confirmé l'envoi."
                    ),
                )

                return False

        except Exception as error:
            cls._mark_failed(
                distributions=distributions,
                error=str(error),
            )

            return False

        cls._mark_sent(
            distributions=distributions,
        )

        return True

    @staticmethod
    def _build_addresses(
        *,
        distributions: list[
            CommunicationMessageRecipient
        ],
        purpose: str,
    ) -> list[str]:
        """
        Retourne les adresses correspondant
        au type de diffusion demandé.

        Les doublons sont supprimés tout en
        conservant l'ordre initial.
        """

        addresses = []
        seen = set()

        for distribution in distributions:

            if distribution.purpose != purpose:
                continue

            email = (
                distribution.destination_email
                or ""
            ).strip().lower()

            if not email:
                continue

            if email in seen:
                continue

            seen.add(
                email
            )

            addresses.append(
                email
            )

        return addresses

    @staticmethod
    def _build_subject(
        *,
        message: CommunicationMessage,
    ) -> str:
        """
        Construit l'objet du mail.

        La référence projet permet le classement
        et la recherche dans les logiciels de messagerie.
        """

        project = (
            message.conversation.project
        )

        subject = (
            message.subject
            or "Communication projet"
        ).strip()

        return (
            f"[{project.reference}] "
            f"{subject}"
        )

    @staticmethod
    def _build_body(
        *,
        message: CommunicationMessage,
    ) -> str:
        """
        Construit le corps texte du mail.

        Le corps correspond volontairement
        au texte saisi par l'utilisateur.

        Les informations projet, diffusion et auteur
        ne sont pas répétées inutilement.
        """

        return (
            message.body
            or ""
        ).strip()

    @staticmethod
    def _attach_files(
        *,
        email: EmailMessage,
        message: CommunicationMessage,
    ) -> None:
        """
        Ajoute au mail les fichiers directement déposés
        dans la communication.
        """

        attachments = (
            message.attachments
            .all()
            .order_by(
                "created_at",
            )
        )

        for attachment in attachments:

            if not attachment.uploaded_file:
                continue

            attachment.uploaded_file.open(
                "rb"
            )

            try:
                content = (
                    attachment.uploaded_file.read()
                )

            finally:
                attachment.uploaded_file.close()

            email.attach(
                filename=(
                    attachment.original_filename
                    or "piece-jointe"
                ),
                content=content,
                mimetype=(
                    attachment.mime_type
                    or "application/octet-stream"
                ),
            )

    @staticmethod
    @transaction.atomic
    def _mark_sent(
        *,
        distributions: list[
            CommunicationMessageRecipient
        ],
    ) -> None:
        """
        Marque toutes les distributions du mail
        comme envoyées.
        """

        now = timezone.now()

        distribution_ids = [
            distribution.pk
            for distribution in distributions
        ]

        (
            CommunicationMessageRecipient.objects
            .filter(
                pk__in=distribution_ids,
                status=(
                    CommunicationMessageRecipient
                    .Status
                    .PENDING
                ),
            )
            .update(
                status=(
                    CommunicationMessageRecipient
                    .Status
                    .SENT
                ),
                sent_at=now,
                error_details="",
            )
        )

    @staticmethod
    @transaction.atomic
    def _mark_failed(
        *,
        distributions: list[
            CommunicationMessageRecipient
        ],
        error: str,
    ) -> None:
        """
        Marque les distributions concernées
        comme étant en échec.
        """

        max_length = (
            CommunicationMessageRecipient
            ._meta
            .get_field(
                "error_details"
            )
            .max_length
        )

        error_details = (
            error
            or "Erreur d'envoi inconnue."
        )[:max_length]

        distribution_ids = [
            distribution.pk
            for distribution in distributions
        ]

        (
            CommunicationMessageRecipient.objects
            .filter(
                pk__in=distribution_ids,
            )
            .update(
                status=(
                    CommunicationMessageRecipient
                    .Status
                    .FAILED
                ),
                error_details=error_details,
            )
        )