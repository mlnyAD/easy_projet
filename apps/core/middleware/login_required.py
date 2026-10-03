

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse


class LoginRequiredMiddleware:
    """
    Redirige les utilisateurs non authentifiés vers la connexion.

    Toute URL applicative est protégée par défaut. Les exceptions sont
    limitées à la connexion, à l'administration et aux fichiers servis
    directement par Django en développement.
    """

    def __init__(
        self,
        get_response,
    ) -> None:
        self.get_response = get_response

    def __call__(
        self,
        request,
    ):
        if (
            request.user.is_authenticated
            or self.is_public_path(
                request.path_info,
            )
        ):
            return self.get_response(
                request,
            )

        return redirect_to_login(
            request.get_full_path(),
            login_url=reverse(
                settings.LOGIN_URL,
            ),
        )

    @staticmethod
    def is_public_path(path: str) -> bool:
        if path.startswith("/documents/versions/"):
            return (
                path.endswith("/content/")
                or path.endswith("/callback/")
                or "/cad-content/" in path
            )

        public_prefixes = (
            reverse(settings.LOGIN_URL),
            "/admin/",
            settings.STATIC_URL,
            settings.MEDIA_URL,
        )

        return any(
            prefix and path.startswith(prefix)
            for prefix in public_prefixes
        )