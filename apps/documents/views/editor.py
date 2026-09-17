

from __future__ import annotations

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.http import (
    Http404,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.views import View

from apps.documents.integrations import (
    DocumentCapability,
    DocumentIntegrationResolver,
)
from apps.documents.models import DocumentVersion
from apps.documents.services import (
    DocumentEditLockService,
)
from apps.projects.services.access import (
    ProjectAccessService,
)
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)


class DocumentEditorView(
    LoginRequiredMixin,
    View,
):
    """
    Ouvre une version documentaire dans l'éditeur configuré
    pour la société du projet.
    """

    template_name = (
        "documents/document_editor.html"
    )

    def get(
        self,
        request,
        *,
        version_id,
    ):
        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(
                request.user
            )
        )

        version = get_object_or_404(
            DocumentVersion.objects
            .select_related(
                "document",
                "document__project",
                "document__project__company",
                "document__current_version",
            )
            .filter(
                document__project__in=(
                    accessible_projects
                ),
            ),
            pk=version_id,
        )

        document = version.document

        if (
            document.current_version_id
            != version.pk
        ):
            raise Http404(
                "Cette version n'est plus "
                "la version courante du document."
            )

        company = document.project.company

        can_work_on_project = (
            ProjectAuthorizationService
            .can_work_on_project(
                user=request.user,
                project=document.project,
            )
        )

        read_only_due_to_lock = False
        read_only_due_to_permission = False
        edit_lock_owner = None
        heartbeat_url = None

        if can_work_on_project:
            lock_result = (
                DocumentEditLockService.acquire(
                    document=document,
                    version=version,
                    user=request.user,
                )
            )

            if lock_result.acquired:
                capability = (
                    DocumentCapability.OFFICE_EDIT
                )

                heartbeat_url = reverse(
                    "documents:version-edit-lock-refresh",
                    kwargs={
                        "version_id": version.pk,
                    },
                )
            else:
                capability = (
                    DocumentCapability.OFFICE_VIEW
                )

                read_only_due_to_lock = True
                edit_lock_owner = lock_result.owner
        else:
            capability = (
                DocumentCapability.OFFICE_VIEW
            )

            read_only_due_to_permission = True

        resolver = DocumentIntegrationResolver()

        try:
            integration = (
                resolver.resolve_for_company(
                    version=version,
                    capability=capability,
                    company=company,
                )
            )
        except LookupError as exc:
            raise Http404(
                "Aucun éditeur compatible "
                "n'est configuré pour ce document."
            ) from exc

        return_path = reverse(
            "documents:folder",
            kwargs={
                "project_id": document.project_id,
                "folder_id": document.folder_id,
            },
        )

        return_url = request.build_absolute_uri(
            return_path
        )

        editor = integration.open(
            version=version,
            capability=capability,
            user=request.user,
            return_url=return_url,
        )

        return render(
            request,
            self.template_name,
            {
                "document": document,
                "version": version,
                "editor": editor,
                "onlyoffice_api_url": (
                    editor["api_url"]
                ),
                "onlyoffice_config": (
                    editor["config"]
                ),
                "read_only_due_to_lock": (
                    read_only_due_to_lock
                ),
                "read_only_due_to_permission": (
                    read_only_due_to_permission
                ),
                "edit_lock_owner": (
                    edit_lock_owner
                ),
                "edit_lock_heartbeat_url": (
                    heartbeat_url
                ),
            },
        )


class DocumentEditLockRefreshView(
    LoginRequiredMixin,
    View,
):
    """
    Renouvelle le verrou d'édition détenu par
    l'utilisateur connecté.
    """

    http_method_names = [
        "post",
    ]

    def post(
        self,
        request,
        *,
        version_id,
    ):
        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(
                request.user
            )
        )

        version = get_object_or_404(
            DocumentVersion.objects
            .select_related(
                "document",
                "document__project",
                "document__current_version",
            )
            .filter(
                document__project__in=(
                    accessible_projects
                ),
            ),
            pk=version_id,
        )

        document = version.document

        if not (
            ProjectAuthorizationService
            .can_work_on_project(
                user=request.user,
                project=document.project,
            )
        ):
            return HttpResponseForbidden(
                "Vous ne pouvez pas modifier ce document."
            )

        if (
            document.current_version_id
            != version.pk
        ):
            return JsonResponse(
                {
                    "ok": False,
                    "reason": "version_not_current",
                },
                status=409,
            )

        refreshed = (
            DocumentEditLockService.refresh(
                document=document,
                user=request.user,
            )
        )

        if not refreshed:
            return JsonResponse(
                {
                    "ok": False,
                    "reason": "lock_not_owned",
                },
                status=409,
            )

        return JsonResponse(
            {
                "ok": True,
            }
        )