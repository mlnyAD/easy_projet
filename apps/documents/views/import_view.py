

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views import View
from pathlib import Path
from apps.catalogs.models import CatalogValue
from apps.documents.forms_import import (
    DocumentImportForm,
)
from apps.documents.models import DocumentFolder
from apps.documents.services import DocumentService
from apps.documents.views.mixins import (
    ProjectDocumentWorkMixin,
)


class DocumentImportView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Import d'un fichier dans un dossier documentaire.
    """

    template_name = (
        "documents/document_import.html"
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
        folder = self.get_folder(project)

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
        folder = self.get_folder(project)

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

        uploaded_files = form.cleaned_data["files"]

        lifecycle = get_object_or_404(
            CatalogValue,
            catalog_type__code="DOCUMENT_LIFECYCLE",
            catalog_type__is_active=True,
            code="ACTIVE",
            is_active=True,
        )

        document_service = DocumentService()

        for uploaded_file in uploaded_files:
            mime_type = (
                getattr(
                    uploaded_file,
                    "content_type",
                    "",
                )
                or "application/octet-stream"
            )

            document_service.import_document(
                project=project,
                folder=folder,
                title=Path(
                    uploaded_file.name
                ).stem,
                description=form.cleaned_data[
                    "description"
                ],
                document_type=None,
                status=None,
                lifecycle=lifecycle,
                content=uploaded_file,
                original_filename=uploaded_file.name,
                mime_type=mime_type,
                user=request.user,
                is_doe=form.cleaned_data["is_doe"],
            )

        file_count = len(uploaded_files)

        messages.success(
            request,
            (
                "Le fichier a été importé."
                if file_count == 1
                else f"{file_count} fichiers ont été importés."
            ),
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=folder.pk,
        )