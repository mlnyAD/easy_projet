

from django.db import models


class DocumentCapability(models.TextChoices):
    """
    Capacités pouvant être demandées à une intégration documentaire.

    Une capacité décrit un besoin fonctionnel.
    Elle ne désigne jamais un fournisseur particulier.
    """

    OFFICE_EDIT = (
        "OFFICE_EDIT",
        "Édition bureautique",
    )

    OFFICE_VIEW = (
        "OFFICE_VIEW",
        "Visualisation bureautique",
    )

    CAD_VIEW = (
        "CAD_VIEW",
        "Visualisation CAO",
    )

    PDF_VIEW = (
        "PDF_VIEW",
        "Visualisation PDF",
    )

    IMAGE_VIEW = (
        "IMAGE_VIEW",
        "Visualisation image",
    )

    MEDIA_PLAY = (
        "MEDIA_PLAY",
        "Lecture audio/vidéo",
    )

    SIGN = (
        "SIGN",
        "Signature électronique",
    )