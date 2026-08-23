

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views import View

from apps.documents.models import DocumentFolder
from apps.documents.services import DocumentFolderService
from apps.projects.models import Project
from django.contrib import messages


class DocumentFolderCreateView(
    LoginRequiredMixin,
    View,
):
    """
    Création d'un dossier documentaire.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
    ) -> HttpResponse:
        project = get_object_or_404(
            Project,
            pk=project_id,
        )

        name = request.POST.get(
            "name",
            "",
        )

        parent_id = request.POST.get(
            "parent_id"
        )

        parent = None

        if parent_id:
            parent = get_object_or_404(
                DocumentFolder,
                pk=parent_id,
                project=project,
                is_active=True,
            )

        try:
            folder = (
                DocumentFolderService
                .create_folder(
                    project=project,
                    parent=parent,
                    name=name,
                )
            )
        except ValueError as exc:
            return HttpResponseBadRequest(
                str(exc)
            )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=folder.pk,
        )


class DocumentFolderRenameView(
    LoginRequiredMixin,
    View,
):
    """
    Renommage d'un dossier documentaire.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        folder_id,
    ) -> HttpResponse:
        project = get_object_or_404(
            Project,
            pk=project_id,
        )

        folder = get_object_or_404(
            DocumentFolder,
            pk=folder_id,
            project=project,
            is_active=True,
        )

        name = request.POST.get(
            "name",
            "",
        )

        try:
            (
                DocumentFolderService
                .rename_folder(
                    folder=folder,
                    name=name,
                )
            )
        except ValueError as exc:
            return HttpResponseBadRequest(
                str(exc)
            )

        return redirect(
            "documents:folder",
            project_id=project.pk,
            folder_id=folder.pk,
        )


class DocumentFolderDeleteView(
    LoginRequiredMixin,
    View,
):
    """
    Suppression d'un dossier documentaire vide.
    """

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
        folder_id,
    ) -> HttpResponse:
        project = get_object_or_404(
            Project,
            pk=project_id,
        )

        folder = get_object_or_404(
            DocumentFolder.objects.select_related(
                "parent",
            ),
            pk=folder_id,
            project=project,
            is_active=True,
        )

        parent = folder.parent

        try:
            DocumentFolderService.delete_folder(
                folder=folder,
            )

            messages.success(
                request,
                "Le répertoire a été supprimé.",
            )

        except ValueError as exc:
            messages.error(
                request,
                str(exc),
            )

            return redirect(
                "documents:folder",
                project_id=project.pk,
                folder_id=folder.pk,
            )

        if parent is not None:
            return redirect(
                "documents:folder",
                project_id=project.pk,
                folder_id=parent.pk,
            )

        return redirect(
            "documents:explorer",
            project_id=project.pk,
        )