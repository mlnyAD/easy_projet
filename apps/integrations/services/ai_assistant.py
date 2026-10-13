

from __future__ import annotations

from apps.integrations.services.openai_services import (
    OpenAIIntegrationService,
)


class AIAssistantService:
    """
    Assistant transversal d'Easy Projet.

    Il répond aux questions générales, sans accéder aux données
    métier d'un projet ou d'un document.
    """

    MAX_HISTORY_MESSAGES = 6
    MAX_MESSAGE_LENGTH = 1_500

    @classmethod
    def answer_general_question(
        cls,
        *,
        question: str,
        history: list[dict[str, str]],
    ) -> str:
        """
        Répond à une question générale sur Easy Projet.
        """

        conversation = cls._format_history(history)

        return OpenAIIntegrationService.generate_text(
            instructions=(
                "Vous êtes l'assistant d'Easy Projet, logiciel de "
                "gestion de projets de construction. Répondez en "
                "français, de façon claire et concise. "
                "Vous pouvez expliquer les fonctionnalités, proposer "
                "une méthode de travail ou demander une précision. "
                "N'inventez jamais de données de projet, de document "
                "ou d'utilisateur. Vous formulez des conseils : vous "
                "ne réalisez aucune modification dans l'application."
            ),
            input_text=(
                f"{conversation}\n\n"
                "Question de l'utilisateur :\n"
                f"{question}"
            ),
        )

    @classmethod
    def _format_history(
        cls,
        history: list[dict[str, str]],
    ) -> str:
        messages: list[str] = []

        for message in history[-cls.MAX_HISTORY_MESSAGES:]:
            role = message["role"]
            content = message["content"]

            label = (
                "Utilisateur"
                if role == "user"
                else "Assistant"
            )

            messages.append(
                f"{label} : {content}"
            )

        if not messages:
            return "Aucun échange précédent."

        return "\n".join(messages)
    