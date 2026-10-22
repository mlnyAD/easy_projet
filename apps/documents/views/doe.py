

from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    redirect,
    render,
)
from django.urls import reverse
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views import View

from apps.documents.forms_doe import DoeGenerateForm
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
    Prépare puis génère ou rafraîchit le DOE d'un projet.
    """

    template_name = "documents/doe_generate_form.html"

    def get(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        form = DoeGenerateForm(
            project=project,
        )

        return self.render_form(
            request=request,
            project=project,
            form=form,
        )

    def post(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        form = DoeGenerateForm(
            request.POST,
            project=project,
        )

        if not form.is_valid():
            return self.render_form(
                request=request,
                project=project,
                form=form,
            )

        doe_template = form.cleaned_data[
            "doe_template"
        ]

        try:
            generation = DoeService().generate(
                project=project,
                user=request.user,
                doe_template=doe_template,
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
            elif doe_template is None:
                messages.success(
                    request,
                    (
                        "Le DOE a été généré avec "
                        f"{generation.document_count} document"
                        f"{'s' if generation.document_count > 1 else ''}."
                    ),
                )
            else:
                messages.success(
                    request,
                    (
                        "Le DOE a été généré à partir du "
                        f'modèle « {doe_template.name} » avec '
                        f"{generation.document_count} document"
                        f"{'s' if generation.document_count > 1 else ''} "
                        "à classer."
                    ),
                )

        return redirect(
            self.get_return_url(
                request=request,
                project=project,
            )
        )

    def render_form(
        self,
        *,
        request,
        project,
        form: DoeGenerateForm,
    ):
        return render(
            request,
            self.template_name,
            {
                "project": project,
                "form": form,
                "has_available_templates": (
                    form.has_available_templates
                ),
                "return_url": self.get_return_url(
                    request=request,
                    project=project,
                ),
            },
        )

    @staticmethod
    def get_return_url(
        *,
        request,
        project,
    ) -> str:
        candidate = (
            request.POST.get("next")
            or request.GET.get("next")
        )

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