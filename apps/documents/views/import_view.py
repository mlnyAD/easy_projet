

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views import View

from apps.catalogs.models import CatalogValue
from apps.documents.forms_import import (
    DocumentImportForm,
)
from apps.documents.models import DocumentFolder
from apps.documents.services import DocumentService
from apps.documents.views.mixins import (
    ProjectDocumentAccessMixin,
)


class DocumentImportView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
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

        lifecycle = get_object_or_404(
            CatalogValue,
            catalog_type__code="DOCUMENT_LIFECYCLE",
            catalog_type__is_active=True,
            code="ACTIVE",
            is_active=True,
        )

        mime_type = (
            getattr(
                uploaded_file,
                "content_type",
                "",
            )
            or "application/octet-stream"
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
            lifecycle=lifecycle,
            content=uploaded_file,
            original_filename=(
                uploaded_file.name
            ),
            mime_type=mime_type,
            user=request.user,
            is_doe=form.cleaned_data[
                "is_doe"
            ],
        )

        messages.success(
            request,
            "Le fichier a été importé.",
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=folder.pk,
        )