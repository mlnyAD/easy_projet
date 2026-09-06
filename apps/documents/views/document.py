

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views import View

from apps.documents.models import (
    Document,
    DocumentFolder,
)
from apps.documents.services import (
    DocumentFavoriteService,
    DocumentService,
)
from apps.documents.views.mixins import (
    ProjectDocumentAccessMixin,
)
        
class DocumentRenameView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    View,
):
    """
    Renommage fonctionnel d'un document.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        document_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )

        document = get_object_or_404(
            Document.objects.select_related(
                "folder",
                "current_version",
            ),
            pk=document_id,
            project=project,
        )

        title = request.POST.get(
            "title",
            "",
        )

        try:
            DocumentService.rename_document(
                document=document,
                title=title,
                user=request.user,
            )

        except ValueError as exc:
            messages.error(
                request,
                str(exc),
            )

        else:
            messages.success(
                request,
                "Le document a été renommé.",
            )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=document.folder_id,
        )


class DocumentMoveView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    View,
):
    """
    Déplacement d'un document dans l'arborescence.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        document_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )

        document = get_object_or_404(
            Document.objects.select_related(
                "folder",
                "current_version",
            ),
            pk=document_id,
            project=project,
        )

        destination_id = request.POST.get(
            "destination_id",
            "",
        )

        destination = get_object_or_404(
            DocumentFolder,
            pk=destination_id,
            project=project,
            is_active=True,
        )

        source_folder = document.folder

        try:
            DocumentService.move_document(
                document=document,
                destination=destination,
                user=request.user,
            )

        except ValueError as exc:
            messages.error(
                request,
                str(exc),
            )

            return redirect(
                "documents:folder",
                project_id=project.pk,
                folder_id=source_folder.pk,
            )

        messages.success(
            request,
            "Le document a été déplacé.",
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=destination.pk,
        )


class DocumentCopyView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    View,
):
    """
    Copie un document à partir de sa version courante.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        document_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )

        document = get_object_or_404(
            Document.objects.select_related(
                "folder",
                "current_version",
                "document_type",
                "status",
                "lifecycle",
            ),
            pk=document_id,
            project=project,
        )

        destination_id = request.POST.get(
            "destination_id",
            "",
        )

        title = request.POST.get(
            "title",
            "",
        )

        destination = get_object_or_404(
            DocumentFolder,
            pk=destination_id,
            project=project,
            is_active=True,
        )

        try:
            copied_document = (
                DocumentService()
                .copy_document(
                    document=document,
                    destination=destination,
                    title=title,
                    user=request.user,
                )
            )

        except ValueError as exc:
            messages.error(
                request,
                str(exc),
            )

            return redirect(
                "documents:folder",
                project_id=project.pk,
                folder_id=document.folder_id,
            )

        messages.success(
            request,
            (
                f'Le document "{copied_document.title}" '
                "a été copié."
            ),
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=destination.pk,
        )


class DocumentFavoriteAddView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    View,
):
    """
    Ajoute un document aux favoris de l'utilisateur.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        document_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )

        document = get_object_or_404(
            Document.objects.select_related(
                "folder",
            ),
            pk=document_id,
            project=project,
        )

        DocumentFavoriteService.add_favorite(
            user=request.user,
            document=document,
        )

        messages.success(
            request,
            "Le document a été ajouté aux favoris.",
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=document.folder_id,
        )


class DocumentFavoriteRemoveView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    View,
):
    """
    Retire un document des favoris de l'utilisateur.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        document_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )

        document = get_object_or_404(
            Document.objects.select_related(
                "folder",
            ),
            pk=document_id,
            project=project,
        )

        DocumentFavoriteService.remove_favorite(
            user=request.user,
            document=document,
        )

        messages.success(
            request,
            "Le document a été retiré des favoris.",
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=document.folder_id,
        )


class DocumentDeleteView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    View,
):
    """
    Suppression définitive d'un document.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        document_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )
        
        document = get_object_or_404(
            Document.objects.select_related(
                "folder",
            ),
            pk=document_id,
            project=project,
        )

        folder_id = document.folder_id
        title = document.title

        try:
            DocumentService().delete_document(
                document=document,
            )

        except Exception:
            messages.error(
                request,
                "Le document n'a pas pu être supprimé.",
            )

            return redirect(
                "documents:folder",
                project_id=project.pk,
                folder_id=folder_id,
            )

        messages.success(
            request,
            f'Le document "{title}" a été supprimé.',
        )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=folder_id,
        )