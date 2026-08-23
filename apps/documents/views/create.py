

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views import View

from apps.documents.forms import DocumentCreateForm
from apps.documents.services import DocumentService
from apps.projects.models import Project


class DocumentCreateView(
    LoginRequiredMixin,
    View,
):
    """
    Création d'un document natif Easy Projet.
    """

    template_name = (
        "documents/document_form.html"
    )

    def get_project(
        self,
        project_id,
    ):
        return get_object_or_404(
            Project.objects.select_related(
                "company",
            ),
            pk=project_id,
        )

    def get(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id
        )

        form = DocumentCreateForm(
            project=project
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
            project_id
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

        service = DocumentService()

        document = service.create_document(
            project=project,
            folder=form.cleaned_data[
                "folder"
            ],
            title=form.cleaned_data[
                "title"
            ],
            document_format=form.cleaned_data[
                "document_format"
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
            user=request.user,
            is_doe=form.cleaned_data[
                "is_doe"
            ],
        )

        document.refresh_from_db()

        version = (
            document.current_version
        )

        return redirect(
            "documents:version-edit",
            version_id=version.pk,
        )