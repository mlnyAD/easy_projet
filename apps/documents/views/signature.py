

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views import View

from apps.documents.forms_signature import (
    SignatureRequestCreateForm,
)
from apps.documents.integrations import (
    DocumentCapability,
    DocumentIntegrationResolver,
)
from apps.documents.services import (
    SignatureArtifactService,
    SignatureService,
)
from apps.documents.storage import get_document_storage
from apps.documents.views.mixins import (
    ProjectDocumentWorkMixin,
)


class SignatureRequestCreateView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Prépare puis envoie une demande de signature électronique.
    """

    template_name = (
        "documents/signature_request_form.html"
    )

    def get(
        self,
        request: HttpRequest,
        *,
        project_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )

        form = SignatureRequestCreateForm(
            project=project,
            initial_document_ids=(
                request.GET.getlist("document")
            ),
            initial=self.get_initial(
                request=request,
            ),
        )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "project": project,
                "return_url": self.get_return_url(
                    request=request,
                    project=project,
                ),
            },
        )

    def post(
        self,
        request: HttpRequest,
        *,
        project_id,
    ) -> HttpResponse:
        project = self.get_project(
            project_id=project_id,
        )

        form = SignatureRequestCreateForm(
            request.POST,
            project=project,
        )

        return_url = self.get_return_url(
            request=request,
            project=project,
        )

        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "project": project,
                    "return_url": return_url,
                },
            )

        versions = tuple(
            document.current_version
            for document in form.cleaned_data["documents"]
        )

        try:
            resolved_integration = (
                DocumentIntegrationResolver()
                .resolve_configured_for_company(
                    version=versions[0],
                    capability=DocumentCapability.SIGN,
                    company=project.company,
                )
            )

            storage = get_document_storage()

            signature_service = SignatureService(
                artifact_service=SignatureArtifactService(
                    storage=storage,
                ),
            )

            signature_request = (
                signature_service.create_draft(
                    project=project,
                    versions=versions,
                    recipients=(
                        form.cleaned_data[
                            "recipient_inputs"
                        ]
                    ),
                    external_integration=(
                        resolved_integration
                        .external_integration
                    ),
                    title=form.cleaned_data["title"],
                    user=request.user,
                )
            )

            signature_service.send_draft(
                signature_request=signature_request,
            )

        except (LookupError, ValueError) as exc:
            form.add_error(None, str(exc))

            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "project": project,
                    "return_url": return_url,
                },
            )

        messages.success(
            request,
            "La demande de signature a été envoyée.",
        )

        return redirect(return_url)

    @staticmethod
    def get_initial(
        *,
        request: HttpRequest,
    ) -> dict:
        initial = {}

        document_ids = request.GET.getlist("document")

        if len(document_ids) == 1:
            initial["title"] = "Demande de signature"

        return initial

    @staticmethod
    def get_return_url(
        *,
        request: HttpRequest,
        project,
    ) -> str:
        candidate = (
            request.POST.get("next")
            or request.GET.get("next")
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
            "documents:explorer",
            kwargs={
                "project_id": project.pk,
            },
        )