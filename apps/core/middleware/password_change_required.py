

from __future__ import annotations

from django.shortcuts import redirect
from django.urls import (
    Resolver404,
    resolve,
)


class PasswordChangeRequiredMiddleware:
    """
    Empêche un utilisateur authentifié d'accéder
    à l'application tant que son mot de passe
    provisoire n'a pas été remplacé.
    """

    ALLOWED_VIEW_NAMES = {
        "users:password-change-required",
        "users:logout",
    }

    def __init__(
        self,
        get_response,
    ):
        self.get_response = get_response

    def __call__(
        self,
        request,
    ):
        user = getattr(
            request,
            "user",
            None,
        )

        if (
            user is None
            or not user.is_authenticated
            or not user.must_change_password
        ):
            return self.get_response(
                request
            )

        try:
            match = resolve(
                request.path_info
            )
        except Resolver404:
            return self.get_response(
                request
            )

        if (
            match.view_name
            in self.ALLOWED_VIEW_NAMES
        ):
            return self.get_response(
                request
            )

        return redirect(
            "users:password-change-required"
        )