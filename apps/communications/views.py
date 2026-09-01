

from __future__ import annotations

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View

from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessageAttachment,
    CommunicationMessageRecipient,
)
from apps.communications.services import (
    CommunicationService,
)
from apps.projects.models import (
    Project,
    ProjectExternalParticipant,
)
from apps.projects.services.access import (
    ProjectAccessService,
)
from apps.users.models import User


class ProjectCommunicationMessageCreateView(
    LoginRequiredMixin,
    View,
):
    """
    Ajout d'une communication au fil d'un projet.

    Une communication peut être distribuée simultanément :

    - à des utilisateurs Easy Projet par messagerie interne ;
    - à des intervenants externes par email.

    Chaque destinataire possède son propre rôle :
    - ACTION ;
    - INFORMATION.

    Les pièces jointes sont enregistrées avant
    toute tentative d'envoi email.

    La distribution email est réalisée après validation
    de la transaction métier.
    """

    http_method_names = [
        "post",
    ]

    def post(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> JsonResponse:
        project = self.get_project()

        subject = (
            request.POST.get(
                "subject",
                "",
            )
            or ""
        )

        body = (
            request.POST.get(
                "body",
                "",
            )
            or ""
        )

        internal_ids = request.POST.getlist(
            "internal_recipients"
        )

        external_ids = request.POST.getlist(
            "external_recipients"
        )

        internal_recipients = (
            self.get_internal_recipients(
                project=project,
                recipient_ids=internal_ids,
            )
        )

        external_recipients = (
            self.get_external_recipients(
                project=project,
                recipient_ids=external_ids,
            )
        )

        if (
            len(internal_recipients)
            != len(set(internal_ids))
        ):
            return JsonResponse(
                {
                    "ok": False,
                    "error": (
                        "Un ou plusieurs destinataires internes "
                        "ne sont pas autorisés pour ce projet."
                    ),
                },
                status=400,
            )

        if (
            len(external_recipients)
            != len(set(external_ids))
        ):
            return JsonResponse(
                {
                    "ok": False,
                    "error": (
                        "Un ou plusieurs intervenants externes "
                        "ne sont pas autorisés pour ce projet."
                    ),
                },
                status=400,
            )

        if (
            not internal_recipients
            and not external_recipients
        ):
            return JsonResponse(
                {
                    "ok": False,
                    "error": (
                        "Au moins un destinataire "
                        "doit être sélectionné."
                    ),
                },
                status=400,
            )

        recipient_purposes = {}

        for recipient in internal_recipients:
            recipient_purposes[
                str(recipient.pk)
            ] = (
                request.POST.get(
                    (
                        "recipient_purpose_"
                        f"{recipient.pk}"
                    ),
                    "INFORMATION",
                )
                or "INFORMATION"
            )

        for recipient in external_recipients:
            recipient_purposes[
                str(recipient.pk)
            ] = (
                request.POST.get(
                    (
                        "recipient_purpose_"
                        f"{recipient.pk}"
                    ),
                    "INFORMATION",
                )
                or "INFORMATION"
            )

        uploaded_files = (
            request.FILES.getlist(
                "attachments"
            )
        )

        try:
            with transaction.atomic():

                conversation = (
                    self.get_or_create_conversation(
                        project=project,
                    )
                )

                message = (
                    CommunicationService
                    .send_project_message(
                        conversation=conversation,
                        author=request.user,
                        subject=subject,
                        body=body,
                        internal_recipients=(
                            internal_recipients
                        ),
                        external_recipients=(
                            external_recipients
                        ),
                        recipient_purposes=(
                            recipient_purposes
                        ),
                    )
                )

                for uploaded_file in uploaded_files:

                    attachment = (
                        CommunicationMessageAttachment(
                            message=message,
                            uploaded_file=(
                                uploaded_file
                            ),
                            original_filename=(
                                uploaded_file.name
                            ),
                            mime_type=(
                                uploaded_file.content_type
                                or ""
                            ),
                            file_size=(
                                uploaded_file.size
                            ),
                            uploaded_by=request.user,
                        )
                    )

                    attachment.full_clean()
                    attachment.save()

        except ValidationError as error:
            return JsonResponse(
                {
                    "ok": False,
                    "error": (
                        self.get_validation_message(
                            error
                        )
                    ),
                },
                status=400,
            )

        # --------------------------------------------------------------
        # Rechargement du message pour le rendu du fil
        # --------------------------------------------------------------

        message = (
            message.__class__.objects
            .select_related(
                "author",
                "imported_by",
            )
            .prefetch_related(
                "attachments",
                "recipients",
                "recipients__user",
                "recipients__external_participant",
            )
            .get(
                pk=message.pk,
            )
        )

        message_html = render_to_string(
            "communications/message.html",
            {
                "message": message,
                "request": request,
            },
            request=request,
        )

        return JsonResponse(
            {
                "ok": True,
                "message": {
                    "id": str(
                        message.pk
                    ),
                    "html": message_html,
                },
            }
        )

    def get_project(self) -> Project:
        """
        Retourne le projet uniquement s'il est accessible
        à l'utilisateur connecté.
        """

        return get_object_or_404(
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            ),
            pk=self.kwargs[
                "project_pk"
            ],
        )

    def get_internal_recipients(
        self,
        *,
        project: Project,
        recipient_ids: list[str],
    ) -> list[User]:
        """
        Retourne les utilisateurs Easy Projet sélectionnés.

        Seuls les utilisateurs actifs disposant d'une
        affectation active au projet sont acceptés.
        """

        if not recipient_ids:
            return []

        return list(
            User.objects
            .filter(
                pk__in=recipient_ids,
                is_active=True,
                project_memberships__project=project,
                project_memberships__is_active=True,
            )
            .exclude(
                pk=self.request.user.pk,
            )
            .distinct()
            .order_by(
                "last_name",
                "first_name",
            )
        )

    def get_external_recipients(
        self,
        *,
        project: Project,
        recipient_ids: list[str],
    ) -> list[
        ProjectExternalParticipant
    ]:
        """
        Retourne les intervenants externes sélectionnés.

        Un intervenant converti en utilisateur Easy Projet
        n'est plus considéré comme destinataire externe.
        """

        if not recipient_ids:
            return []

        return list(
            ProjectExternalParticipant.objects
            .filter(
                pk__in=recipient_ids,
                project=project,
                is_active=True,
                converted_user__isnull=True,
            )
            .exclude(
                email="",
            )
            .order_by(
                "last_name",
                "first_name",
            )
        )

    def get_or_create_conversation(
        self,
        *,
        project: Project,
    ) -> CommunicationConversation:
        """
        Retourne le fil principal actif du projet.

        La conversation n'est créée qu'au premier message.
        """

        conversation = (
            CommunicationConversation.objects
            .filter(
                project=project,
                is_active=True,
            )
            .order_by(
                "created_at",
            )
            .first()
        )

        if conversation is not None:
            return conversation

        conversation = (
            CommunicationConversation(
                project=project,
                title="Communications du projet",
                created_by=self.request.user,
            )
        )

        conversation.full_clean()
        conversation.save()

        return conversation

    @staticmethod
    def get_validation_message(
        error: ValidationError,
    ) -> str:
        """
        Transforme une ValidationError métier
        en message exploitable par le panneau.
        """

        if hasattr(
            error,
            "message_dict",
        ):
            messages = []

            for values in (
                error.message_dict.values()
            ):
                messages.extend(
                    values
                )

            if messages:
                return " ".join(
                    str(message)
                    for message in messages
                )

        if error.messages:
            return " ".join(
                str(message)
                for message in error.messages
            )

        return (
            "Le message n'a pas pu être envoyé."
        )


class CommunicationAttachmentDownloadView(
    LoginRequiredMixin,
    View,
):
    """
    Téléchargement protégé d'une pièce jointe.

    L'utilisateur doit avoir accès au projet auquel
    appartient la communication.
    """

    http_method_names = [
        "get",
    ]

    def get(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ):
        accessible_projects = (
            ProjectAccessService
            .get_accessible_projects(
                request.user
            )
        )

        attachment = get_object_or_404(
            CommunicationMessageAttachment.objects
            .select_related(
                "message",
                "message__conversation",
            )
            .filter(
                message__conversation__project__in=(
                    accessible_projects
                ),
            ),
            pk=self.kwargs["pk"],
        )

        if not attachment.uploaded_file:
            raise Http404(
                "Le fichier joint n'est pas disponible."
            )

        try:
            file_handle = (
                attachment.uploaded_file.open(
                    "rb"
                )
            )

        except (
            FileNotFoundError,
            OSError,
        ) as error:
            raise Http404(
                "Le fichier joint est introuvable."
            ) from error

        return FileResponse(
            file_handle,
            as_attachment=True,
            filename=(
                attachment.original_filename
                or "piece-jointe"
            ),
            content_type=(
                attachment.mime_type
                or "application/octet-stream"
            ),
        )


class ProjectCommunicationMarkReadView(
    LoginRequiredMixin,
    View,
):
    """
    Marque comme lues les communications internes
    du projet destinées à l'utilisateur connecté.
    """

    http_method_names = [
        "post",
    ]

    def post(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> JsonResponse:
        project = get_object_or_404(
            ProjectAccessService
            .get_accessible_projects(
                request.user
            ),
            pk=self.kwargs[
                "project_pk"
            ],
        )

        now = timezone.now()

        updated_count = (
            CommunicationMessageRecipient.objects
            .filter(
                user=request.user,
                channel=(
                    CommunicationMessageRecipient
                    .Channel
                    .INTERNAL
                ),
                read_at__isnull=True,
                message__is_active=True,
                message__conversation__project=project,
            )
            .update(
                status=(
                    CommunicationMessageRecipient
                    .Status
                    .READ
                ),
                read_at=now,
            )
        )

        return JsonResponse(
            {
                "ok": True,
                "marked_read": updated_count,
            }
        )