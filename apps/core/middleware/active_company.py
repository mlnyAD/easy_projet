

from __future__ import annotations


class ActiveCompanyMiddleware:
    """
    Détermine la société active pour la requête courante.

    Version actuelle :
    - utilisateur authentifié -> société de l'utilisateur ;
    - utilisateur non authentifié -> aucune société active.

    Ce point d'entrée pourra évoluer plus tard vers :
    - société choisie en session ;
    - société du projet courant ;
    - autre règle de contexte.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.active_company = self._resolve_active_company(
            request
        )

        return self.get_response(request)

    @staticmethod
    def _resolve_active_company(request):
        user = getattr(
            request,
            "user",
            None,
        )

        if (
            user is None
            or not user.is_authenticated
        ):
            return None

        return getattr(
            user,
            "company",
            None,
        )