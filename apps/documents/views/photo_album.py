

from __future__ import annotations

from uuid import UUID
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from apps.documents.models import Document, DocumentVersion
from apps.projects.models import Project
from apps.projects.services.access import ProjectAccessService


class ProjectPhotoAlbumView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Visionneuse des images présentes dans la documentation
    d'un projet, quel que soit leur dossier.
    """

    template_name = "documents/photo_album.html"

    def get_project(self) -> Project:
        return get_object_or_404(
            ProjectAccessService.get_accessible_projects(
                self.request.user
            ),
            pk=self.kwargs["project_id"],
        )

    def get_photo_documents(
        self,
        project: Project,
    ) -> tuple[Document, ...]:
        return tuple(
            Document.objects.filter(
                project=project,
                current_version__technical_type=(
                    DocumentVersion.TechnicalType.IMAGE
                ),
            )
            .select_related(
                "folder",
                "current_version",
            )
            .order_by(
                "-current_version__created_at",
                "-created_at",
            )
        )

    def get_selected_document_id(self) -> UUID | None:
        raw_document_id = self.request.GET.get(
            "photo",
            "",
        ).strip()

        if not raw_document_id:
            return None

        try:
            return UUID(raw_document_id)
        except ValueError:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        photos = self.get_photo_documents(project)

        selected_document_id = self.get_selected_document_id()

        selected_photo = next(
            (
                photo
                for photo in photos
                if photo.pk == selected_document_id
            ),
            photos[0] if photos else None,
        )

        context.update(
            {
                "project": project,
                "photos": photos,
                "selected_photo": selected_photo,
                "project_workspace_url": reverse(
                    "projects:workspace",
                    kwargs={"pk": project.pk},
                ),
            }
        )

        return context