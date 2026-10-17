

from __future__ import annotations

from pathlib import Path

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.urls import reverse
from django.views.generic import FormView

from framework.form import FormMode
from framework.integrations.django.views.form import (
    EPFormView,
)

from apps.catalogs.models import CatalogValue
from apps.documents.form_definition import (
    DOCUMENT_IMPORT_FORM_DEFINITION,
)
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
    EPFormView,
    FormView,
):
    """
    Import d'un ou plusieurs fichiers dans un dossier documentaire.
    """

    form_class = DocumentImportForm
    definition = DOCUMENT_IMPORT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_form_mode(self):
        return FormMode.CREATE

    def get_project_instance(self):
        return self.get_project()

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

    def get_cancel_url(self) -> str:
        project = self.get_project_instance()
        folder = self.get_folder(project)

        return reverse(
            "documents:folder",
            kwargs={
                "project_id": project.pk,
                "folder_id": folder.pk,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project_instance()

        context.update(
            {
                "project": project,
                "folder": self.get_folder(project),
            }
        )

        return context

    def form_valid(self, form):
        project = self.get_project_instance()
        folder = self.get_folder(project)

        lifecycle = get_object_or_404(
            CatalogValue,
            catalog_type__code="DOCUMENT_LIFECYCLE",
            catalog_type__is_active=True,
            code="ACTIVE",
            is_active=True,
        )

        document_service = DocumentService()

        uploaded_files = form.cleaned_data["files"]

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
                user=self.request.user,
                is_doe=form.cleaned_data["is_doe"],
            )

        file_count = len(uploaded_files)

        messages.success(
            self.request,
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