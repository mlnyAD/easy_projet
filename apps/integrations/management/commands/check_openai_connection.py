

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from apps.integrations.services.openai_services import (
    OpenAIIntegrationError,
    OpenAIIntegrationService,
)


class Command(BaseCommand):
    help = (
        "Vérifie la connexion à OpenAI avec la configuration locale."
    )

    def handle(self, *args, **options):
        try:
            answer = (
                OpenAIIntegrationService
                .check_connection()
            )
        except OpenAIIntegrationError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(
            self.style.SUCCESS(
                "Connexion OpenAI opérationnelle."
            )
        )
        self.stdout.write(
            f"Réponse du modèle : {answer}"
        )