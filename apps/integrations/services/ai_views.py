

from __future__ import annotations

import json

from django.http import JsonResponse
from django.views import View

from apps.integrations.services.ai_assistant import (
    AIAssistantService,
)
from apps.integrations.services.openai_services import (
    OpenAIIntegrationError,
)


class AIAssistantView(View):
    """
    Répond aux demandes générales adressées à l'assistant IA.
    """

    MAX_QUESTION_LENGTH = 1_500
    MAX_HISTORY_MESSAGES = 6
    MAX_HISTORY_MESSAGE_LENGTH = 1_500

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self._error_response(
                "Vous devez être authentifié."
            )

        if not request.user.is_active:
            return self._error_response(
                "Votre compte n'est pas actif."
            )

        payload = self._get_payload(request)

        if payload is None:
            return self._error_response(
                "La requête IA est invalide."
            )

        question = (
            payload.get("question")
            or ""
        ).strip()

        if not question:
            return self._error_response(
                "Saisissez une demande pour l'assistant."
            )

        if len(question) > self.MAX_QUESTION_LENGTH:
            return self._error_response(
                "Votre demande ne peut pas dépasser "
                "1 500 caractères."
            )

        history = self._normalize_history(
            payload.get("history")
        )

        try:
            answer = (
                AIAssistantService
                .answer_general_question(
                    question=question,
                    history=history,
                )
            )
        except OpenAIIntegrationError:
            return JsonResponse(
                {
                    "error": (
                        "L'assistant IA est temporairement "
                        "indisponible."
                    ),
                },
                status=502,
            )

        return JsonResponse(
            {
                "answer": answer,
            }
        )

    @staticmethod
    def _get_payload(request) -> dict | None:
        try:
            payload = json.loads(
                request.body.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            return None

        return payload if isinstance(payload, dict) else None

    def _normalize_history(
        self,
        value,
    ) -> list[dict[str, str]]:
        if not isinstance(value, list):
            return []

        messages: list[dict[str, str]] = []

        for item in value[-self.MAX_HISTORY_MESSAGES:]:
            if not isinstance(item, dict):
                continue

            role = item.get("role")
            content = item.get("content")

            if role not in {"user", "assistant"}:
                continue

            if not isinstance(content, str):
                continue

            content = content.strip()

            if not content:
                continue

            messages.append(
                {
                    "role": role,
                    "content": content[
                        :self.MAX_HISTORY_MESSAGE_LENGTH
                    ],
                }
            )

        return messages

    @staticmethod
    def _error_response(message: str) -> JsonResponse:
        return JsonResponse(
            {
                "error": message,
            },
            status=400,
        )