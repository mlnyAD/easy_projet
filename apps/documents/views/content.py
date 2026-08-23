

from __future__ import annotations

import json

from django.http import (
    FileResponse,
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.views import View

from apps.documents.integrations.providers import (
    OnlyOfficeCallbackError,
    OnlyOfficeCallbackService,
    OnlyOfficeDownloadError,
    OnlyOfficeJwtService,
)
from apps.documents.models import DocumentVersion
from apps.documents.services.access_token_service import (
    DocumentAccessTokenService,
)
from apps.documents.storage import get_document_storage
from django.contrib.auth.mixins import LoginRequiredMixin


class DocumentVersionContentView(View):
    """
    Fournit le contenu physique d'une version documentaire.

    Cette vue est destinée notamment aux outils externes
    comme ONLYOFFICE.

    L'accès est protégé par un jeton temporaire signé.
    """

    def get(
        self,
        request,
        *,
        version_id,
    ):
        version = get_object_or_404(
            DocumentVersion.objects.select_related(
                "document",
            ),
            pk=version_id,
        )

        token = request.GET.get(
            "token",
            "",
        )

        if not DocumentAccessTokenService.validate_token(
            token=token,
            version=version,
        ):
            return HttpResponseForbidden(
                "Jeton documentaire invalide ou expiré."
            )

        storage = get_document_storage()

        if not storage.exists(
            version.storage_key
        ):
            raise Http404(
                "Fichier documentaire introuvable."
            )

        content = storage.open(
            version.storage_key
        )

        response = FileResponse(
            content,
            content_type=(
                version.mime_type
                or "application/octet-stream"
            ),
        )

        response["Content-Disposition"] = (
            'inline; '
            f'filename="{version.original_filename}"'
        )

        response["Content-Length"] = str(
            version.file_size
        )

        return response


class DocumentVersionCallbackView(View):
    """
    Point de retour ONLYOFFICE pour une version documentaire.

    Le callback est authentifié par le JWT partagé
    entre ONLYOFFICE et Easy Projet.

    Lorsqu'ONLYOFFICE retourne le statut 2,
    le fichier modifié est récupéré puis enregistré
    comme une nouvelle DocumentVersion.
    """

    http_method_names = [
        "post",
    ]

    def post(
        self,
        request,
        *,
        version_id,
    ):
        version = get_object_or_404(
            DocumentVersion.objects.select_related(
                "document",
            ),
            pk=version_id,
        )

        # --------------------------------------------------------------
        # Authentification JWT ONLYOFFICE
        # --------------------------------------------------------------

        token = self._get_token(
            request
        )

        if not token:
            return JsonResponse(
                {
                    "error": 1,
                },
                status=403,
            )

        jwt_payload = (
            OnlyOfficeJwtService.try_decode(
                token
            )
        )

        if jwt_payload is None:
            return JsonResponse(
                {
                    "error": 1,
                },
                status=403,
            )

        # --------------------------------------------------------------
        # Lecture du payload ONLYOFFICE
        # --------------------------------------------------------------

        try:
            payload = json.loads(
                request.body.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            return HttpResponseBadRequest(
                "Payload ONLYOFFICE invalide."
            )

        if not isinstance(
            payload,
            dict,
        ):
            return HttpResponseBadRequest(
                "Payload ONLYOFFICE invalide."
            )

        # --------------------------------------------------------------
        # Validation minimale
        # --------------------------------------------------------------

        status = payload.get(
            "status"
        )

        if not isinstance(
            status,
            int,
        ):
            return HttpResponseBadRequest(
                "Statut ONLYOFFICE manquant ou invalide."
            )

        # --------------------------------------------------------------
        # Traitement métier
        # --------------------------------------------------------------

        try:
            OnlyOfficeCallbackService().process(
                version=version,
                payload=payload,
            )

        except (
            OnlyOfficeCallbackError,
            OnlyOfficeDownloadError,
        ):
            return JsonResponse(
                {
                    "error": 1,
                },
                status=500,
            )

        return JsonResponse(
            {
                "error": 0,
            }
        )

    @staticmethod
    def _get_token(
        request,
    ) -> str:
        """
        Extrait le JWT ONLYOFFICE de l'en-tête Authorization.

        Format attendu :

            Authorization: Bearer <token>
        """

        authorization = (
            request.headers.get(
                "Authorization",
                "",
            )
            .strip()
        )

        if not authorization:
            return ""

        scheme, separator, token = (
            authorization.partition(
                " "
            )
        )

        if (
            not separator
            or scheme.lower() != "bearer"
        ):
            return ""

        return token.strip()
    
class DocumentVersionView(
    LoginRequiredMixin,
    View,
):
    """
    Affiche une version documentaire à un utilisateur
    authentifié Easy Projet.

    Utilisé notamment pour l'affichage natif des PDF.
    """

    def get(
        self,
        request,
        *,
        version_id,
    ):
        version = get_object_or_404(
            DocumentVersion.objects.select_related(
                "document",
                "document__project",
            ),
            pk=version_id,
        )

        storage = get_document_storage()

        if not storage.exists(
            version.storage_key
        ):
            raise Http404(
                "Fichier documentaire introuvable."
            )

        content = storage.open(
            version.storage_key
        )

        response = FileResponse(
            content,
            content_type=(
                version.mime_type
                or "application/octet-stream"
            ),
        )

        response["Content-Disposition"] = (
            'inline; '
            f'filename="{version.original_filename}"'
        )

        response["Content-Length"] = str(
            version.file_size
        )

        return response


class DocumentVersionDownloadView(
    LoginRequiredMixin,
    View,
):
    """
    Télécharge une version documentaire.
    """

    def get(
        self,
        request,
        *,
        version_id,
    ):
        version = get_object_or_404(
            DocumentVersion.objects.select_related(
                "document",
                "document__project",
            ),
            pk=version_id,
        )

        storage = get_document_storage()

        if not storage.exists(
            version.storage_key
        ):
            raise Http404(
                "Fichier documentaire introuvable."
            )

        content = storage.open(
            version.storage_key
        )

        response = FileResponse(
            content,
            content_type=(
                version.mime_type
                or "application/octet-stream"
            ),
        )

        response["Content-Disposition"] = (
            'attachment; '
            f'filename="{version.original_filename}"'
        )

        response["Content-Length"] = str(
            version.file_size
        )

        return response    