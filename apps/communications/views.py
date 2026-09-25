

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
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
from django.views.generic import TemplateView

from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessage,
    CommunicationMessageAttachment,
    CommunicationMessageRecipient,
)
from apps.communications.services import CommunicationService
from apps.projects.services.access import ProjectAccessService
from apps.users.models import User


class CommunicationInboxView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Vue pleine page conservée comme point d'accès secondaire.

    Le volet droit constitue l'accès habituel à la messagerie.
    """

    template_name = "communications/inbox.html"

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs,
        )

        context["conversations"] = (
            CommunicationConversation.objects
            .filter(
                is_active=True,
            )
            .filter(
                Q(
                    messages__author=self.request.user,
                )
                | Q(
                    messages__recipients__user=self.request.user,
                )
            )
            .prefetch_related(
                "projects",
            )
            .distinct()
            .order_by(
                "-updated_at",
                "-created_at",
            )
        )

        return context


class CommunicationMessageCreateView(
    LoginRequiredMixin,
    View,
):
    """
    Création d'un message personnel depuis le volet global.

    Les destinataires internes sont des utilisateurs actifs
    de la même société que l'expéditeur.

    Les projets constituent seulement un contexte facultatif.
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
        internal_ids = request.POST.getlist(
            "internal_recipients"
        )
        project_ids = request.POST.getlist(
            "projects"
        )

        try:
            internal_recipients = (
                self.get_internal_recipients(
                    recipient_ids=internal_ids,
                )
            )

            projects = self.get_projects(
                project_ids=project_ids,
            )

            if (
                len(internal_recipients)
                != len(set(internal_ids))
            ):
                raise ValidationError(
                    {
                        "recipients": (
                            "Un ou plusieurs destinataires "
                            "internes ne sont pas autorisés."
                        ),
                    }
                )

            if len(projects) != len(set(project_ids)):
                raise ValidationError(
                    {
                        "projects": (
                            "Un ou plusieurs projets "
                            "ne sont pas accessibles."
                        ),
                    }
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
                        (
                            CommunicationMessageRecipient
                            .Purpose
                            .INFORMATION
                        ),
                    )
                    or (
                        CommunicationMessageRecipient
                        .Purpose
                        .INFORMATION
                    )
                )

            with transaction.atomic():
                conversation = (
                    CommunicationService
                    .create_conversation(
                        author=request.user,
                        title=(
                            request.POST.get(
                                "subject",
                                "",
                            )
                            or ""
                        ),
                        projects=projects,
                    )
                )

                message = (
                    CommunicationService
                    .send_message(
                        conversation=conversation,
                        author=request.user,
                        subject=(
                            request.POST.get(
                                "subject",
                                "",
                            )
                            or ""
                        ),
                        body=(
                            request.POST.get(
                                "body",
                                "",
                            )
                            or ""
                        ),
                        internal_recipients=(
                            internal_recipients
                        ),
                        recipient_purposes=(
                            recipient_purposes
                        ),
                    )
                )

                self.create_attachments(
                    request=request,
                    message=message,
                )

        except ValidationError as error:
            return JsonResponse(
                {
                    "ok": False,
                    "error": self.get_validation_message(
                        error
                    ),
                },
                status=400,
            )

        message = (
            CommunicationMessage.objects
            .select_related(
                "author",
                "imported_by",
                "conversation",
            )
            .prefetch_related(
                "conversation__projects",
                "attachments",
                "recipients",
                "recipients__user",
                "recipients__external_participant",
            )
            .get(
                pk=message.pk,
            )
        )

        return JsonResponse(
            {
                "ok": True,
                "message": {
                    "id": str(message.pk),
                    "html": render_to_string(
                        "communications/message.html",
                        {
                            "message": message,
                            "request": request,
                        },
                        request=request,
                    ),
                },
            }
        )

    def get_internal_recipients(
        self,
        *,
        recipient_ids: list[str],
    ) -> list[User]:
        if not recipient_ids:
            return []

        return list(
            User.objects
            .filter(
                pk__in=recipient_ids,
                company=self.request.user.company,
                is_active=True,
            )
            .exclude(
                pk=self.request.user.pk,
            )
            .order_by(
                "last_name",
                "first_name",
            )
        )

    def get_projects(
        self,
        *,
        project_ids: list[str],
    ) -> list:
        if not project_ids:
            return []

        return list(
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            )
            .filter(
                pk__in=project_ids,
            )
            .order_by(
                "reference",
            )
        )

    @staticmethod
    def create_attachments(
        *,
        request: HttpRequest,
        message: CommunicationMessage,
    ) -> None:
        for uploaded_file in request.FILES.getlist(
            "attachments"
        ):
            attachment = (
                CommunicationMessageAttachment(
                    message=message,
                    uploaded_file=uploaded_file,
                    original_filename=uploaded_file.name,
                    mime_type=(
                        uploaded_file.content_type
                        or ""
                    ),
                    file_size=uploaded_file.size,
                    uploaded_by=request.user,
                )
            )

            attachment.full_clean()
            attachment.save()

    @staticmethod
    def get_validation_message(
        error: ValidationError,
    ) -> str:
        if hasattr(
            error,
            "message_dict",
        ):
            messages = []

            for values in (
                error.message_dict.values()
            ):
                messages.extend(values)

            if messages:
                return " ".join(
                    str(message)
                    for message in messages
                )

        return " ".join(
            str(message)
            for message in error.messages
        )


class CommunicationMarkReadView(
    LoginRequiredMixin,
    View,
):
    """
    Marque comme lus les messages internes personnels
    non lus de l'utilisateur connecté.
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
                message__conversation__is_active=True,
            )
            .update(
                status=(
                    CommunicationMessageRecipient
                    .Status
                    .READ
                ),
                read_at=timezone.now(),
            )
        )

        return JsonResponse(
            {
                "ok": True,
                "marked_read": updated_count,
            }
        )


class CommunicationAttachmentDownloadView(
    LoginRequiredMixin,
    View,
):
    """
    Téléchargement sécurisé d'une pièce jointe.

    L'auteur ou un destinataire interne du message
    peut télécharger la pièce jointe.
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
        attachment = get_object_or_404(
            CommunicationMessageAttachment.objects
            .select_related(
                "message",
                "message__conversation",
            )
            .filter(
                Q(
                    message__author=request.user,
                )
                | Q(
                    message__recipients__user=request.user,
                )
            )
            .distinct(),
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