

from __future__ import annotations

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import (
    redirect,
    render,
)
from django.urls import reverse
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.views import View

from apps.documents.forms_doe import DoeGenerateForm
from apps.documents.services import DoeService
from apps.documents.views.mixins import (
    ProjectDocumentWorkMixin,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.documents.models import (
    DocumentFolder,
    DoeClassificationProposal,
    DoeGeneration,
    DoeClassificationProposalItem,
)
from apps.documents.services import (
    DoeClassificationError,
    DoeClassificationService,
    DoeService,
)


class DoeGenerateView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Prépare puis génère ou rafraîchit le DOE d'un projet.
    """

    template_name = "documents/doe_generate_form.html"

    def get(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        form = DoeGenerateForm(
            project=project,
        )

        return self.render_form(
            request=request,
            project=project,
            form=form,
        )

    def post(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        form = DoeGenerateForm(
            request.POST,
            project=project,
        )

        if not form.is_valid():
            return self.render_form(
                request=request,
                project=project,
                form=form,
            )

        doe_template = form.cleaned_data[
            "doe_template"
        ]

        try:
            generation = DoeService().generate(
                project=project,
                user=request.user,
                doe_template=doe_template,
            )
        except ValueError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            if generation is None:
                messages.warning(
                    request,
                    "Aucun document ou dossier n'est "
                    "sélectionné pour le DOE.",
                )
            elif doe_template is None:
                messages.success(
                    request,
                    (
                        "Le DOE a été généré avec "
                        f"{generation.document_count} document"
                        f"{'s' if generation.document_count > 1 else ''}."
                    ),
                )
            else:
                messages.success(
                    request,
                    (
                        "Le DOE a été généré à partir du "
                        f'modèle « {doe_template.name} » avec '
                        f"{generation.document_count} document"
                        f"{'s' if generation.document_count > 1 else ''} "
                        "à classer."
                    ),
                )

        return redirect(
            self.get_return_url(
                request=request,
                project=project,
            )
        )

    def render_form(
        self,
        *,
        request,
        project,
        form: DoeGenerateForm,
    ):
        return render(
            request,
            self.template_name,
            {
                "project": project,
                "form": form,
                "has_available_templates": (
                    form.has_available_templates
                ),
                "return_url": self.get_return_url(
                    request=request,
                    project=project,
                ),
            },
        )

    @staticmethod
    def get_return_url(
        *,
        request,
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
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
        ):
            return candidate

        explorer_url = reverse(
            "documents:explorer",
            kwargs={
                "project_id": project.pk,
            },
        )

        return (
            f"{explorer_url}?"
            f"{urlencode({'workspace': 'doe'})}"
        )


class DoeClassificationProposalCreateView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Demande à l'IA une proposition de classement du DOE.

    Cette action ne déplace aucun document.
    """

    def post(
        self,
        request,
        *,
        project_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        generation = (
            DoeGeneration.objects
            .filter(
                project=project,
            )
            .select_related(
                "doe_root_folder",
                "doe_template",
            )
            .order_by("-created_at")
            .first()
        )

        if generation is None:
            messages.error(
                request,
                "Aucun DOE n'a encore été généré pour ce projet.",
            )
            return redirect(
                DoeGenerateView.get_return_url(
                    request=request,
                    project=project,
                )
            )

        try:
            proposal = (
                DoeClassificationService()
                .create_proposal(
                    doe_generation=generation,
                    user=request.user,
                )
            )
        except DoeClassificationError as exc:
            messages.error(
                request,
                str(exc),
            )
            return redirect(
                DoeGenerateView.get_return_url(
                    request=request,
                    project=project,
                )
            )

        messages.success(
            request,
            (
                "La proposition de classement IA a été créée. "
                "Aucun document n'a été déplacé."
            ),
        )

        return redirect(
            "documents:doe-classification-proposal-detail",
            project_id=project.pk,
            proposal_id=proposal.pk,
        )


class DoeClassificationProposalDetailView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Affiche une proposition de classement IA.

    La consultation est volontairement sans effet de bord.
    """

    template_name = (
        "documents/doe_classification_proposal_detail.html"
    )

    def get(
        self,
        request,
        *,
        project_id,
        proposal_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        proposal = get_object_or_404(
            DoeClassificationProposal.objects
            .select_related(
                "doe_generation",
                "doe_generation__doe_template",
                "requested_by",
            )
            .prefetch_related(
                "items__document",
                "items__document__current_version",
                "items__proposed_folder",
            ),
            pk=proposal_id,
            project=project,
        )

        explorer_url = reverse(
            "documents:explorer",
            kwargs={
                "project_id": project.pk,
            },
        )

        try:
            target_folders = (
                DoeClassificationService()
                .get_available_target_folders(
                    doe_generation=proposal.doe_generation,
                )
            )
        except DoeClassificationError:
            target_folders = ()
            
        return render(
            request,
            self.template_name,
            {
                "project": project,
                "proposal": proposal,
                "target_folders": target_folders,
                "return_url": (
                    f"{explorer_url}?"
                    f"{urlencode({'workspace': 'doe'})}"
                ),
            },
        )


class DoeClassificationProposalItemApplyView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Valide ou corrige une proposition de classement IA.
    """

    def post(
        self,
        request,
        *,
        project_id,
        proposal_id,
        item_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        item = get_object_or_404(
            DoeClassificationProposalItem.objects
            .select_related(
                "proposal",
                "document",
            ),
            pk=item_id,
            proposal_id=proposal_id,
            proposal__project=project,
        )

        destination_id = request.POST.get(
            "destination_id",
            "",
        )

        destination = get_object_or_404(
            DocumentFolder,
            pk=destination_id,
            project=project,
        )

        try:
            DoeClassificationService().apply_item(
                item=item,
                destination=destination,
                user=request.user,
            )
        except DoeClassificationError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            messages.success(
                request,
                "Le document DOE a été classé.",
            )

        return redirect(
            "documents:doe-classification-proposal-detail",
            project_id=project.pk,
            proposal_id=proposal_id,
        )


class DoeClassificationProposalItemRejectView(
    LoginRequiredMixin,
    ProjectDocumentWorkMixin,
    View,
):
    """
    Refuse une proposition de classement IA.
    """

    def post(
        self,
        request,
        *,
        project_id,
        proposal_id,
        item_id,
    ):
        project = self.get_project(
            project_id=project_id,
        )

        item = get_object_or_404(
            DoeClassificationProposalItem.objects,
            pk=item_id,
            proposal_id=proposal_id,
            proposal__project=project,
        )

        try:
            DoeClassificationService().reject_item(
                item=item,
                user=request.user,
            )
        except DoeClassificationError as exc:
            messages.error(
                request,
                str(exc),
            )
        else:
            messages.success(
                request,
                "La proposition a été refusée.",
            )

        return redirect(
            "documents:doe-classification-proposal-detail",
            project_id=project.pk,
            proposal_id=proposal_id,
        )    