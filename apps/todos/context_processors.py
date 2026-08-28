

from __future__ import annotations

from django.db.models import Q

from apps.todos.models import TodoAction


def todo_context(request):
    """
    Fournit les informations Todo disponibles globalement
    dans les templates Easy Projet.

    Le context processor doit rester utilisable même lorsqu'une
    HttpRequest technique ne possède pas d'utilisateur, notamment
    dans certains tests unitaires du framework.
    """

    user = getattr(
        request,
        "user",
        None,
    )

    if (
        user is None
        or not user.is_authenticated
    ):
        return {
            "todo_pending_count": 0,
        }

    todo_pending_count = (
        TodoAction.objects
        .filter(
            Q(
                owner=user,
                origin=TodoAction.Origin.PERSONAL,
            )
            | Q(
                recipients__user=user,
                origin=TodoAction.Origin.ASSIGNED,
            ),
            status__in=(
                TodoAction.Status.TODO,
                TodoAction.Status.IN_PROGRESS,
                TodoAction.Status.SUSPENDED,
            ),
        )
        .distinct()
        .count()
    )

    return {
        "todo_pending_count": todo_pending_count,
    }