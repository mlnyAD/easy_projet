

from __future__ import annotations

from django import template

from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessageRecipient,
)
from apps.projects.models import (
    ProjectExternalParticipant,
)
from apps.users.models import User


register = template.Library()


@register.simple_tag(
    takes_context=True,
)
def communication_unread_count(
    context,
    project=None,
) -> int:
    """
    Retourne le nombre de communications internes
    non lues par l'utilisateur connecté.

    Si un projet est fourni, le compteur est limité
    à ce projet.
    """

    request = context.get(
        "request"
    )

    if (
        request is None
        or not request.user.is_authenticated
    ):
        return 0

    queryset = (
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
    )

    if project is not None:
        queryset = queryset.filter(
            message__conversation__project=project,
        )

    return queryset.count()


@register.inclusion_tag(
    "communications/panel.html",
    takes_context=True,
)
def communication_panel(
    context,
    project,
):
    """
    Prépare le panneau de communications du projet courant.

    Le rendu n'a volontairement aucun effet de bord :
    aucune conversation n'est créée automatiquement.
    """

    request = context.get("request")

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

    messages = ()

    if conversation is not None:
        messages = (
            conversation.messages
            .filter(
                is_active=True,
            )
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
            .order_by(
                "created_at",
            )
        )

    internal_recipients = (
        User.objects
        .filter(
            is_active=True,
            project_memberships__project=project,
            project_memberships__is_active=True,
        )
        .exclude(
            pk=(
                request.user.pk
                if (
                    request
                    and request.user.is_authenticated
                )
                else None
            ),
        )
        .distinct()
        .order_by(
            "last_name",
            "first_name",
        )
    )

    external_recipients = (
        ProjectExternalParticipant.objects
        .filter(
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

    return {
        "request": request,
        "project": project,
        "conversation": conversation,
        "communication_messages": messages,
        "communication_internal_recipients": (
            internal_recipients
        ),
        "communication_external_recipients": (
            external_recipients
        ),
    }