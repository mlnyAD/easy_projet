

from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views import View

from apps.documents.services import DoeService
from apps.documents.views.mixins import (
    ProjectDocumentWorkMixin,
)


class DoeGenerateView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Génère ou rafraîchit le DOE d'un projet.
    """

    def post(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        try:
            generation = DoeService().generate(
                project=project,
                user=request.user,
            )
        except ValueError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            if generation is None:
                messages.warning(
                    request,
                    "Aucun document ou dossier n'est "
                    "sélectionné pour le DOE.",
                )
            else:
                messages.success(
                    request,
                    (
                        "Le DOE a été généré avec "
                        f"{generation.document_count} document"
                        f"{'s' if generation.document_count > 1 else ''}."
                    ),
                )

        return redirect(
            self.get_return_url(
                request=request,
                project=project,
            )
        )

    @staticmethod
    def get_return_url(
        *,
        request,
        project,
    ) -> str:
        candidate = request.GET.get("next")

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
        ):
            return candidate

        explorer_url = reverse(
            "documents:explorer",
            kwargs={
                "project_id": project.pk,
            },
        )

        return (
            f"{explorer_url}?"
            f"{urlencode({'workspace': 'doe'})}"
        )