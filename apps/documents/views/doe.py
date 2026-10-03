

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
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
            "projects:workspace",
            pk=project.pk,
        )