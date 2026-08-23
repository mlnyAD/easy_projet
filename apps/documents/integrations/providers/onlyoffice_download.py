

from __future__ import annotations

from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OnlyOfficeDownloadError(RuntimeError):
    """
    Erreur lors de la récupération d'un fichier
    depuis ONLYOFFICE.
    """


class OnlyOfficeDownloadService:
    """
    Télécharge un fichier produit par ONLYOFFICE.

    Le service retourne un flux binaire afin qu'il puisse
    être transmis directement au service de versionnement.
    """

    TIMEOUT_SECONDS = 30

    @classmethod
    def download(
        cls,
        url: str,
    ) -> BytesIO:
        normalized_url = url.strip()

        if not normalized_url:
            raise ValueError(
                "L'URL de téléchargement ne peut pas être vide."
            )

        request = Request(
            normalized_url,
            method="GET",
        )

        try:
            with urlopen(
                request,
                timeout=cls.TIMEOUT_SECONDS,
            ) as response:
                content = response.read()

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
        ) as exc:
            raise OnlyOfficeDownloadError(
                "Impossible de récupérer le fichier depuis ONLYOFFICE."
            ) from exc

        return BytesIO(content)