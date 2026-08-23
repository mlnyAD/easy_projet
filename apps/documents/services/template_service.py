

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from django.conf import settings


class DocumentTemplateService:
    """
    Accès aux modèles techniques utilisés pour créer
    les documents bureautiques natifs Easy Projet.
    """

    TEMPLATES = {
        "word": {
            "filename": "empty.docx",
            "extension": ".docx",
            "mime_type": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        },
        "excel": {
            "filename": "empty.xlsx",
            "extension": ".xlsx",
            "mime_type": (
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        },
        "powerpoint": {
            "filename": "empty.pptx",
            "extension": ".pptx",
            "mime_type": (
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
        },
    }

    def __init__(
        self,
        template_root: Path | str | None = None,
    ) -> None:
        self.template_root = Path(
            template_root
            or (
                settings.BASE_DIR
                / "apps"
                / "documents"
                / "templates_files"
            )
        )

    def get_definition(
        self,
        document_format: str,
    ) -> dict[str, str]:
        key = document_format.strip().lower()

        try:
            return self.TEMPLATES[key]
        except KeyError as exc:
            raise ValueError(
                f"Format documentaire non supporté : "
                f"{document_format}"
            ) from exc

    def open_template(
        self,
        document_format: str,
    ) -> BinaryIO:
        definition = self.get_definition(
            document_format
        )

        path = (
            self.template_root
            / definition["filename"]
        )

        if not path.is_file():
            raise FileNotFoundError(
                f"Modèle documentaire introuvable : {path}"
            )

        return path.open("rb")