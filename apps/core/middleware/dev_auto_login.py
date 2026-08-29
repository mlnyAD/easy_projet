
        
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.exceptions import ImproperlyConfigured


class DevelopmentAutoLoginMiddleware:
    """
    Authentifie automatiquement l'utilisateur de développement configuré.

    Ce middleware ne fonctionne que lorsque :
    - DEBUG est actif ;
    - DEV_AUTO_LOGIN est explicitement activé.

    Lorsque l'utilisateur configuré change, la session Django
    est automatiquement basculée vers ce nouvel utilisateur.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        if settings.DEV_AUTO_LOGIN and not settings.DEBUG:
            raise ImproperlyConfigured(
                "DEV_AUTO_LOGIN ne peut pas être activé "
                "lorsque DEBUG est désactivé."
            )

    def __call__(self, request):
        if (
            settings.DEBUG
            and settings.DEV_AUTO_LOGIN
        ):
            self._ensure_development_user(request)

        return self.get_response(request)

    def _ensure_development_user(
        self,
        request,
    ) -> None:
        """
        Garantit que l'utilisateur courant correspond
        à DEV_AUTO_LOGIN_EMAIL.
        """

        email = (
            settings.DEV_AUTO_LOGIN_EMAIL
            .strip()
            .lower()
        )

        if not email:
            raise ImproperlyConfigured(
                "DEV_AUTO_LOGIN_EMAIL doit être renseigné "
                "lorsque DEV_AUTO_LOGIN est actif."
            )

        current_email = (
            getattr(
                request.user,
                "email",
                "",
            )
            or ""
        ).strip().lower()

        if (
            request.user.is_authenticated
            and current_email == email
        ):
            return

        user_model = get_user_model()

        try:
            user = user_model.objects.get(
                email=email,
                is_active=True,
            )
        except user_model.DoesNotExist as error:
            raise ImproperlyConfigured(
                "L'utilisateur de développement configuré "
                f"n'existe pas ou est inactif : {email}"
            ) from error

        login(
            request,
            user,
            backend=(
                "django.contrib.auth.backends."
                "ModelBackend"
            ),
        )