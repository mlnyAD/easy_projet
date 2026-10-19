

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.views import View
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.exceptions import PermissionDenied

from framework.integrations.django.views import EPUpdateView

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
    ProjectDocumentWorkMixin,
)
from apps.documents.forms import DocumentPropertiesForm
from apps.documents.form_definition import (
    DOCUMENT_PROPERTIES_FORM_DEFINITION,
)
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)

def get_document_return_url(
    *,
    request: HttpRequest,
    project,
    folder_id,
) -> str:
    candidate = (
        request.POST.get("next")
        or ""
    ).strip()

    if (
        candidate
        and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={
                request.get_host(),
            },
            require_https=request.is_secure(),
        )
    ):
        return candidate

    return reverse(
        "documents:folder",
        kwargs={
            "project_id": project.pk,
            "folder_id": folder_id,
        },
    )
    

class DocumentPropertiesView(
    ProjectDocumentAccessMixin,
    EPUpdateView,
):
    """
    Consultation et modification des propriétés d'un document.
    """

    model = Document
    form_class = DocumentPropertiesForm
    definition = DOCUMENT_PROPERTIES_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_queryset(self):
        project = self.get_project()

        return (
            Document.objects.filter(
                project=project,
                trashed_at__isnull=True,
            )
            .select_related(
                "folder",
                "current_version",
                "document_type",
                "status",
                "lifecycle",
            )
        )

    def can_edit_object(self) -> bool:
        return (
            ProjectAuthorizationService
            .can_work_on_project(
                user=self.request.user,
                project=self.object.project,
            )
        )

    def get_return_url(self) -> str:
        candidate = (
            self.request.GET.get("next")
            or self.request.POST.get("next")
        )

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={self.request.get_host()},
                require_https=self.request.is_secure(),
            )
        ):
            return candidate

        return reverse(
            "documents:folder",
            kwargs={
                "project_id": self.object.project_id,
                "folder_id": self.object.folder_id,
            },
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Les propriétés du document ont été mises à jour.",
        )

        return response
            

class DocumentRenameView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
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
            trashed_at__isnull=True,
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
            self.get_return_url(
                request=request,
                document=document,
            )
        )

    @staticmethod
    def get_return_url(
        *,
        request: HttpRequest,
        document: Document,
    ) -> str:
        candidate = request.POST.get(
            "next",
        )

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    request.get_host(),
                },
                require_https=request.is_secure(),
            )
        ):
            return candidate

        return reverse(
            "documents:folder",
            kwargs={
                "project_id": document.project_id,
                "folder_id": document.folder_id,
            },
        )

class DocumentMoveView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
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
            trashed_at__isnull=True,
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
                get_document_return_url(
                    request=request,
                    project=project,
                    folder_id=source_folder.pk,
                )
            )

        messages.success(
            request,
            "Le document a été déplacé.",
        )

        return redirect(
            get_document_return_url(
                request=request,
                project=project,
                folder_id=destination.pk,
            )
        )


class DocumentCopyView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
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
            trashed_at__isnull=True,            
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
                get_document_return_url(
                    request=request,
                    project=project,
                    folder_id=document.folder_id,
                )
            )
        messages.success(
            request,
            (
                f'Le document "{copied_document.title}" '
                "a été copié."
            ),
        )

        return redirect(
            get_document_return_url(
                request=request,
                project=project,
                folder_id=destination.pk,
            )
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
            trashed_at__isnull=True,            
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
            get_document_return_url(
                request=request,
                project=project,
                folder_id=document.folder_id,
            )
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
            trashed_at__isnull=True,            
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
            get_document_return_url(
                request=request,
                project=project,
                folder_id=document.folder_id,
            )
        )

class DocumentDeleteView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Met un document source à la corbeille.
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
            is_doe_generated=False,
            trashed_at__isnull=True,
        )

        folder_id = document.folder_id
        title = document.title

        try:
            DocumentService().move_to_trash(
                document=document,
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
                f'Le document "{title}" a été mis à la corbeille.',
            )

        return redirect(
            get_document_return_url(
                request=request,
                project=project,
                folder_id=folder_id,
            )
        )


class DocumentRestoreView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Restaure un document depuis la corbeille.
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
            is_doe_generated=False,
            trashed_at__isnull=False,
        )

        title = document.title

        try:
            DocumentService().restore_document(
                document=document,
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
                f'Le document "{title}" a été restauré.',
            )

        candidate = (
            request.POST.get("next")
            or ""
        ).strip()

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
        ):
            return redirect(candidate)

        return redirect(
            "documents:trash",
            project_id=project.pk,
        )
        
        
class DocumentPermanentDeleteView(
    LoginRequiredMixin,
    ProjectDocumentAccessMixin,
    View,
):
    """
    Supprime définitivement un document placé dans la corbeille.
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

        if not (
            ProjectAuthorizationService
            .can_permanently_delete_document(
                user=request.user,
                project=project,
            )
        ):
            raise PermissionDenied(
                "Vous ne pouvez pas supprimer définitivement "
                "ce document."
            )

        document = get_object_or_404(
            Document.objects.select_related("folder"),
            pk=document_id,
            project=project,
            is_doe_generated=False,
            trashed_at__isnull=False,
        )

        title = document.title

        try:
            DocumentService().delete_document(
                document=document,
            )
        except ValueError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            messages.success(
                request,
                f'Le document "{title}" a été supprimé définitivement.',
            )

        candidate = (
            request.POST.get("next")
            or ""
        ).strip()

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
        ):
            return redirect(candidate)

        return redirect(
            "documents:trash",
            project_id=project.pk,
        )