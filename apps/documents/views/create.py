

from __future__ import annotations

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from framework.form import FormMode
from framework.integrations.django.views.form import (
    EPFormView,
)

from apps.documents.form_definition import (
    DOCUMENT_CREATE_FORM_DEFINITION,
)
from apps.documents.forms import DocumentCreateForm
from apps.documents.services import DocumentService
from apps.documents.views.mixins import (
    ProjectDocumentWorkMixin,
)


class DocumentCreateView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    EPFormView,
    FormView,
):
    """
    Création d'un document natif Easy Projet.
    """

    form_class = DocumentCreateForm
    definition = DOCUMENT_CREATE_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_form_mode(self):
        return FormMode.CREATE

    def get_project_instance(self):
        return self.get_project(
            project_id=self.kwargs["project_id"],
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["project"] = self.get_project_instance()

        return kwargs

    def get_initial(self) -> dict:
        initial = super().get_initial()

        document_format = (
            self.request.GET.get("document_format")
            or ""
        ).strip()

        valid_formats = {
            DocumentCreateForm.FORMAT_WORD,
            DocumentCreateForm.FORMAT_EXCEL,
            DocumentCreateForm.FORMAT_POWERPOINT,
        }

        if document_format in valid_formats:
            initial["document_format"] = document_format

        folder = self.get_selected_folder()

        if folder is not None:
            initial["folder"] = folder.pk

        return initial

    def get_selected_folder(self):
        folder_pk = (
            self.request.POST.get("folder")
            or self.request.GET.get("folder")
            or ""
        ).strip()

        if not folder_pk:
            return None

        return (
            self.get_project_instance()
            .document_folders
            .filter(
                pk=folder_pk,
                is_active=True,
            )
            .first()
        )

    def get_cancel_url(self) -> str:
        project = self.get_project_instance()
        folder = self.get_selected_folder()

        if folder is not None:
            return reverse(
                "documents:folder",
                kwargs={
                    "project_id": project.pk,
                    "folder_id": folder.pk,
                },
            )

        return reverse(
            "documents:explorer",
            kwargs={
                "project_id": project.pk,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["project"] = self.get_project_instance()

        return context

    def form_valid(self, form):
        project = self.get_project_instance()

        document = DocumentService().create_document(
            project=project,
            folder=form.cleaned_data["folder"],
            title=form.cleaned_data["title"],
            document_format=(
                form.cleaned_data["document_format"]
            ),
            document_type=form.cleaned_data["document_type"],
            status=form.cleaned_data["status"],
            lifecycle=form.cleaned_data["lifecycle"],
            user=self.request.user,
            is_doe=form.cleaned_data["is_doe"],
        )

        document.refresh_from_db()

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=document.folder_id,
        )