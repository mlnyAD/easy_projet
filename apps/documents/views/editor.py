

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View

from apps.documents.integrations import (
    DocumentCapability,
    DocumentIntegrationResolver,
)
from apps.documents.models import DocumentVersion


class DocumentEditorView(
    LoginRequiredMixin,
    View,
):
    """
    Ouvre une version documentaire dans l'éditeur
    configuré pour la société du projet.

    La vue ne connaît pas directement ONLYOFFICE :
    le fournisseur est déterminé par
    DocumentIntegrationResolver.
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
        version = get_object_or_404(
            DocumentVersion.objects.select_related(
                "document",
                "document__project",
                "document__project__company",
                "document__current_version",
            ),
            pk=version_id,
        )

        document = version.document

        # --------------------------------------------------------------
        # Une ancienne version reste consultable,
        # mais ne doit pas être rééditée comme si elle était courante.
        # --------------------------------------------------------------

        if (
            document.current_version_id
            != version.pk
        ):
            raise Http404(
                "Cette version n'est plus "
                "la version courante du document."
            )

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
                        DocumentCapability.OFFICE_EDIT
                    ),
                    company=company,
                )
            )
        except LookupError as exc:
            raise Http404(
                "Aucun éditeur compatible "
                "n'est configuré pour ce document."
            ) from exc

        editor = integration.open(
            version=version,
            capability=(
                DocumentCapability.OFFICE_EDIT
            ),
            user=request.user,
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
            },
        )