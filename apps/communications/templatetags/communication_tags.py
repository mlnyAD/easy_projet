

from __future__ import annotations

from django import template
from django.db.models import Q

from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessageRecipient,
)
from apps.projects.services.access import ProjectAccessService
from apps.users.models import User

register = template.Library()


@register.simple_tag(
    takes_context=True,
)
def communication_unread_count(
    context,
) -> int:
    request = context.get("request")

    if (
        request is None
        or not request.user.is_authenticated
    ):
        return 0

    return (
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
        .count()
    )


@register.inclusion_tag(
    "communications/panel.html",
    takes_context=True,
)
def communication_panel(
    context,
    project=None,
):
    """
    Prépare le volet personnel de messagerie.

    Le paramètre ``project`` est conservé pour compatibilité
    avec l'appel existant dans layout/base.html ; il n'est plus
    utilisé pour limiter la messagerie.
    """

    request = context.get("request")

    if (
        request is None
        or not request.user.is_authenticated
    ):
        return {
            "communication_messages": (),
            "communication_conversations": (),
            "communication_internal_recipients": (),
            "communication_projects": (),
        }

    user = request.user

    conversations = (
        CommunicationConversation.objects
        .filter(
            is_active=True,
        )
        .filter(
            Q(messages__author=user)
            | Q(messages__recipients__user=user)
        )
        .select_related(
            "created_by",
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

    messages = (
        user.communication_messages
        .filter(
            is_active=True,
            conversation__is_active=True,
        )
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
        .order_by(
            "created_at",
        )
    )

    received_messages = (
        user.received_communication_messages
        .filter(
            channel=(
                CommunicationMessageRecipient
                .Channel
                .INTERNAL
            ),
            message__is_active=True,
            message__conversation__is_active=True,
        )
        .select_related(
            "message",
            "message__author",
            "message__imported_by",
            "message__conversation",
        )
        .prefetch_related(
            "message__conversation__projects",
            "message__attachments",
            "message__recipients",
            "message__recipients__user",
            "message__recipients__external_participant",
        )
        .order_by(
            "message__created_at",
        )
    )

    visible_message_ids = set(
        messages.values_list(
            "pk",
            flat=True,
        )
    )
    visible_message_ids.update(
        received_messages.values_list(
            "message_id",
            flat=True,
        )
    )

    visible_messages = (
        messages.model.objects
        .filter(
            pk__in=visible_message_ids,
        )
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
        .order_by(
            "created_at",
        )
    )

    internal_recipients = (
        User.objects
        .filter(
            company=user.company,
            is_active=True,
        )
        .exclude(
            pk=user.pk,
        )
        .order_by(
            "last_name",
            "first_name",
        )
    )

    return {
        "request": request,
        "communication_messages": visible_messages,
        "communication_conversations": conversations,
        "communication_internal_recipients": (
            internal_recipients
        ),
        "communication_projects": (
            ProjectAccessService
            .get_accessible_projects(user)
            .order_by("reference")
        ),
    }