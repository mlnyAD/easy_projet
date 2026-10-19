

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views.generic import FormView

from framework.form import FormMode
from framework.integrations.django.views.form import (
    EPFormView,
)

from apps.documents.form_definition import (
    DOCUMENT_SIGNATURE_REQUEST_FORM_DEFINITION,
)
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
    EPFormView,
    FormView,
):
    """
    Prépare puis envoie une demande de signature électronique.
    """

    form_class = SignatureRequestCreateForm
    definition = DOCUMENT_SIGNATURE_REQUEST_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_form_mode(self):
        return FormMode.CREATE

    def get_project_instance(self):
        if not hasattr(
            self,
            "_project_instance",
        ):
            self._project_instance = self.get_project(
                project_id=self.kwargs["project_id"],
            )

        return self._project_instance

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["project"] = self.get_project_instance()

        kwargs["initial_document_ids"] = (
            self.request.GET.getlist("document")
        )

        return kwargs

    def get_initial(self):
        initial = super().get_initial()

        if len(
            self.request.GET.getlist("document")
        ) == 1:
            initial["title"] = "Demande de signature"

        return initial

    def get_return_url(self) -> str:
        candidate = (
            self.request.POST.get("next")
            or self.request.GET.get("next")
            or ""
        ).strip()

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    self.request.get_host(),
                },
                require_https=self.request.is_secure(),
            )
        ):
            return candidate

        return reverse(
            "documents:explorer",
            kwargs={
                "project_id": (
                    self.get_project_instance().pk
                ),
            },
        )

    def get_success_url(self) -> str:
        return self.get_return_url()

    def get_cancel_url(self) -> str:
        return self.get_return_url()

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs,
        )

        project = self.get_project_instance()

        context.update(
            {
                "project": project,
                "form_subtitle": (
                    f"{project.reference} — {project.name}"
                ),
                "form_action_label": "Envoyer à signer",
                "form_action_icon": "send",
            }
        )

        return context

    def form_valid(self, form):
        project = self.get_project_instance()

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

            signature_service = SignatureService(
                artifact_service=SignatureArtifactService(
                    storage=get_document_storage(),
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
                    user=self.request.user,
                )
            )

            signature_service.send_draft(
                signature_request=signature_request,
            )

        except (LookupError, ValueError) as exc:
            form.add_error(
                None,
                str(exc),
            )

            return self.form_invalid(form)

        messages.success(
            self.request,
            "La demande de signature a été envoyée.",
        )

        return redirect(self.get_success_url())