

from __future__ import annotations

from django.conf import settings
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
)


class OpenAIIntegrationError(Exception):
    """Erreur fonctionnelle liée à l'intégration OpenAI."""


class OpenAIIntegrationService:
    """
    Client technique OpenAI.

    La clé est lue uniquement depuis la configuration serveur.
    Elle n'est jamais stockée en base de données ni renvoyée
    au navigateur.
    """

    @classmethod
    def check_connection(cls) -> str:
        """
        Vérifie la disponibilité de l'API OpenAI avec une requête
        minimale et retourne la réponse du modèle.
        """

        return cls.generate_text(
            instructions=(
                "Répondez uniquement par le mot OK."
            ),
            input_text=(
                "Vérifiez que vous pouvez répondre."
            ),
            max_output_tokens=20,
        )

    @classmethod
    def generate_text(
        cls,
        *,
        instructions: str,
        input_text: str,
        max_output_tokens: int = 1_600,
    ) -> str:
        """
        Interroge OpenAI et retourne le texte de réponse.

        Cette méthode centralise les appels IA de l'application.
        """

        client = cls._get_client()

        try:
            response = client.responses.create(
                model=settings.OPENAI_MODEL,
                instructions=instructions,
                input=input_text,
                max_output_tokens=max_output_tokens,
            )
        except AuthenticationError as error:
            raise OpenAIIntegrationError(
                "La clé OpenAI est invalide ou expirée."
            ) from error
        except APIConnectionError as error:
            raise OpenAIIntegrationError(
                "La connexion au service OpenAI a échoué."
            ) from error
        except APIStatusError as error:
            raise OpenAIIntegrationError(
                "Le service OpenAI a retourné une erreur "
                f"HTTP {error.status_code} : {error}"
            ) from error
        except OpenAIError as error:
            raise OpenAIIntegrationError(
                "Une erreur OpenAI est survenue."
            ) from error

        answer = (
            response.output_text
            or ""
        ).strip()

        if not answer:
            raise OpenAIIntegrationError(
                "OpenAI a répondu sans contenu exploitable."
            )

        return answer

    @classmethod
    def _get_client(cls) -> OpenAI:
        api_key = settings.OPENAI_API_KEY
        model = settings.OPENAI_MODEL

        if not api_key:
            raise OpenAIIntegrationError(
                "La variable OPENAI_API_KEY n'est pas configurée."
            )

        if not model:
            raise OpenAIIntegrationError(
                "La variable OPENAI_MODEL n'est pas configurée."
            )

        return OpenAI(
            api_key=api_key,
        )