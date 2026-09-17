

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    redirect,
    render,
)
from django.views import View

from apps.documents.forms import DocumentCreateForm
from apps.documents.services import DocumentService
from apps.documents.views.mixins import (
    ProjectDocumentWorkMixin,
)


class DocumentCreateView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Création d'un document natif Easy Projet.
    """

    template_name = (
        "documents/document_form.html"
    )

    def get(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        form = DocumentCreateForm(
            project=project,
        )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "project": project,
            },
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

        form = DocumentCreateForm(
            request.POST,
            project=project,
        )

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "project": project,
                },
            )

        document = DocumentService().create_document(
            project=project,
            folder=form.cleaned_data["folder"],
            title=form.cleaned_data["title"],
            document_format=(
                form.cleaned_data["document_format"]
            ),
            document_type=(
                form.cleaned_data["document_type"]
            ),
            status=form.cleaned_data["status"],
            lifecycle=form.cleaned_data["lifecycle"],
            user=request.user,
            is_doe=form.cleaned_data["is_doe"],
        )

        document.refresh_from_db()

        return redirect(
            "documents:version-edit",
            version_id=document.current_version.pk,
        )