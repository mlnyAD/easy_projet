

from __future__ import annotations

import time

from django.core.management.base import (
    BaseCommand,
)

from apps.communications.email_service import (
    CommunicationEmailService,
)
from apps.communications.models import (
    CommunicationMessageRecipient,
)


class Command(BaseCommand):
    """
    Worker de distribution des communications email.

    Les distributions EMAIL / PENDING constituent
    la file d'attente persistante.
    """

    help = (
        "Traite les communications email "
        "en attente d'envoi."
    )

    sleep_seconds = 2

    def add_arguments(
        self,
        parser,
    ) -> None:
        parser.add_argument(
            "--once",
            action="store_true",
            help=(
                "Traite les messages actuellement "
                "en attente puis termine."
            ),
        )

        parser.add_argument(
            "--sleep",
            type=float,
            default=self.sleep_seconds,
            help=(
                "Délai entre deux recherches "
                "de messages en attente."
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ) -> None:
        once = options[
            "once"
        ]

        sleep_seconds = max(
            options["sleep"],
            0.5,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Worker Communications email démarré."
            )
        )

        while True:

            processed_count = (
                self.process_pending_messages()
            )

            if once:
                break

            if processed_count == 0:
                time.sleep(
                    sleep_seconds
                )

    def process_pending_messages(
        self,
    ) -> int:
        """
        Traite une fois chaque communication
        disposant d'au moins une distribution
        EMAIL / PENDING.
        """

        message_ids = list(
            CommunicationMessageRecipient.objects
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
                message__is_active=True,
                message__conversation__is_active=True,
            )
            .values_list(
                "message_id",
                flat=True,
            )
            .distinct()
            .order_by(
                "message_id",
            )
        )

        for message_id in message_ids:

            success = (
                CommunicationEmailService
                .send_pending_message(
                    message_id=message_id,
                )
            )

            if success:

                self.stdout.write(
                    self.style.SUCCESS(
                        (
                            "Communication "
                            f"{message_id} envoyée."
                        )
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        (
                            "Communication "
                            f"{message_id} non envoyée."
                        )
                    )
                )

        return len(
            message_ids
        )