

from __future__ import annotations
from django.db import models
from django.db.models import (
    Case,
    CharField,
    Exists,
    OuterRef,
    Q,
    QuerySet,
    Value,
    When,
)

from apps.todos.models import (
    TodoAction,
    TodoActionRecipient,
)
from apps.users.models import User


def get_user_todo_actions(
    *,
    user: User,
) -> QuerySet[TodoAction]:
    """
    Retourne les actions appartenant au Todo
    d'un utilisateur.

    Sont incluses :
    - ses actions personnelles ;
    - les actions qui lui sont assignées.

    Les libellés nécessaires à l'affichage
    sont ajoutés au queryset.
    """

    recipient_for_user = (
        TodoActionRecipient.objects
        .filter(
            action_id=OuterRef("pk"),
            user=user,
        )
    )

    return (
        TodoAction.objects
        .filter(
            Q(owner=user)
            | Q(recipients__user=user)
        )
        .select_related(
            "owner",
            "project",
            "context_content_type",
        )
        .prefetch_related(
            "recipients",
            "recipients__user",
        )
        .annotate(
            is_recipient=Exists(
                recipient_for_user
            ),
        )
        .annotate(
            is_follow_up=Case(
                When(
                    owner=user,
                    is_recipient=False,
                    origin=TodoAction.Origin.ASSIGNED,
                    then=Value(True),
                ),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
            row_css_class=Case(
                When(
                    is_follow_up=True,
                    then=Value(
                        "ep-row-follow-up"
                    ),
                ),
                default=Value(""),
                output_field=CharField(),
            ),
        )
        .annotate(
            status_label=Case(
                When(
                    status=TodoAction.Status.TODO,
                    then=Value("À faire"),
                ),
                When(
                    status=TodoAction.Status.IN_PROGRESS,
                    then=Value("En cours"),
                ),
                When(
                    status=TodoAction.Status.SUSPENDED,
                    then=Value("Suspendue"),
                ),
                When(
                    status=TodoAction.Status.COMPLETED,
                    then=Value("Terminée"),
                ),
                When(
                    status=TodoAction.Status.ABANDONED,
                    then=Value("Abandonnée"),
                ),
                default=Value(""),
                output_field=CharField(),
            ),

            origin_label=Case(
                When(
                    origin=TodoAction.Origin.PERSONAL,
                    then=Value("Personnelle"),
                ),
                When(
                    origin=TodoAction.Origin.ASSIGNED,
                    then=Value("Assignée"),
                ),
                default=Value(""),
                output_field=CharField(),
            ),

            role_label=Case(
                When(
                    origin=TodoAction.Origin.PERSONAL,
                    then=Value("—"),
                ),
                When(
                    recipients__user=user,
                    recipients__role=(
                        TodoActionRecipient.Role.ACTION
                    ),
                    then=Value("Pour action"),
                ),
                When(
                    recipients__user=user,
                    recipients__role=(
                        TodoActionRecipient.Role.INFORMATION
                    ),
                    then=Value("Pour information"),
                ),
                When(
                    recipients__user=user,
                    recipients__role=(
                        TodoActionRecipient.Role.COLLABORATION
                    ),
                    then=Value("Action commune"),
                ),
                default=Value("—"),
                output_field=CharField(),
            ),
        )
        .distinct()
    )