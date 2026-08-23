

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views import View

from apps.documents.forms_import import (
    DocumentImportForm,
)
from apps.documents.models import DocumentFolder
from apps.documents.services import DocumentService
from apps.projects.models import Project


class DocumentImportView(
    LoginRequiredMixin,
    View,
):
    """
    Import d'un PDF dans un dossier documentaire.
    """

    template_name = (
        "documents/document_import.html"
    )

    def get_project(self):
        return get_object_or_404(
            Project,
            pk=self.kwargs["project_id"],
        )

    def get_folder(
        self,
        project,
    ):
        return get_object_or_404(
            DocumentFolder,
            pk=self.kwargs["folder_id"],
            project=project,
            is_active=True,
        )

    def get(
        self,
        request,
        *,
        project_id,
        folder_id,
    ):
        project = self.get_project()
        folder = self.get_folder(
            project
        )

        form = DocumentImportForm()

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "project": project,
                "folder": folder,
            },
        )

    def post(
        self,
        request,
        *,
        project_id,
        folder_id,
    ):
        project = self.get_project()
        folder = self.get_folder(
            project
        )

        form = DocumentImportForm(
            request.POST,
            request.FILES,
        )

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "project": project,
                    "folder": folder,
                },
            )

        uploaded_file = (
            form.cleaned_data["file"]
        )

        DocumentService().import_document(
            project=project,
            folder=folder,
            title=form.cleaned_data[
                "title"
            ],
            document_type=form.cleaned_data[
                "document_type"
            ],
            status=form.cleaned_data[
                "status"
            ],
            lifecycle=form.cleaned_data[
                "lifecycle"
            ],
            content=uploaded_file,
            original_filename=(
                uploaded_file.name
            ),
            mime_type="application/pdf",
            user=request.user,
            is_doe=form.cleaned_data[
                "is_doe"
            ],
        )

        messages.success(
            request,
            "Le document PDF a été importé.",
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=folder.pk,
        )