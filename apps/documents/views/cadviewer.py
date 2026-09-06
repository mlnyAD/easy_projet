

from __future__ import annotations

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.views import View

from apps.documents.integrations import (
    DocumentCapability,
    DocumentIntegrationResolver,
)
from apps.documents.models import (
    DocumentVersion,
)
from apps.projects.services.access import (
    ProjectAccessService,
)


class DocumentCadViewerView(
    LoginRequiredMixin,
    View,
):
    """
    Ouvre une version CAO dans CADViewer.
    """

    template_name = (
        "documents/document_cadviewer.html"
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
            )
            .filter(
                document__project__in=(
                    accessible_projects
                ),
            ),
            pk=version_id,
        )

        document = version.document

        company = (
            document.project.company
        )

        resolver = (
            DocumentIntegrationResolver()
        )

        try:
            integration = (
                resolver.resolve_for_company(
                    version=version,
                    capability=(
                        DocumentCapability
                        .CAD_VIEW
                    ),
                    company=company,
                )
            )

        except LookupError as exc:
            raise Http404(
                "Aucun visualiseur CAO compatible "
                "n'est configuré pour ce document."
            ) from exc

        viewer = integration.open(
            version=version,
            capability=(
                DocumentCapability
                .CAD_VIEW
            ),
            user=request.user,
        )

        return render(
            request,
            self.template_name,
            {
                "document": (
                    document
                ),
                "version": (
                    version
                ),
                "viewer": (
                    viewer
                ),
            },
        )