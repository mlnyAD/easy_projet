

from __future__ import annotations

from pathlib import Path

from django import template
from django.templatetags.static import static


register = template.Library()


WORD_EXTENSIONS = frozenset(
    {
        ".doc",
        ".docm",
        ".docx",
        ".dot",
        ".dotm",
        ".dotx",
        ".odt",
        ".rtf",
    }
)

SPREADSHEET_EXTENSIONS = frozenset(
    {
        ".csv",
        ".ods",
        ".xls",
        ".xlsb",
        ".xlsm",
        ".xlsx",
    }
)

PRESENTATION_EXTENSIONS = frozenset(
    {
        ".odp",
        ".pot",
        ".potx",
        ".pps",
        ".ppsx",
        ".ppt",
        ".pptm",
        ".pptx",
    }
)

CAD_EXTENSIONS = frozenset(
    {
        ".dwf",
        ".dwg",
        ".dxf",
    }
)

VIDEO_EXTENSIONS = frozenset(
    {
        ".avi",
        ".m4a",
        ".m4v",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".ogg",
        ".ogv",
        ".wav",
        ".webm",
        ".wmv",
    }
)


@register.simple_tag
def document_icon_url(version) -> str:
    """
    Retourne l'URL de l'icône correspondant à une version.
    """

    filename = getattr(
        version,
        "original_filename",
        "",
    )

    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        icon_name = "pdf"
    elif extension in WORD_EXTENSIONS:
        icon_name = "word"
    elif extension in SPREADSHEET_EXTENSIONS:
        icon_name = "xls"
    elif extension in PRESENTATION_EXTENSIONS:
        icon_name = "ppt"
    elif extension in CAD_EXTENSIONS:
        icon_name = "dwg"
    elif extension in VIDEO_EXTENSIONS:
        icon_name = "video"
    else:
        icon_name = "default"

    return static(
        f"documents/images/file-types/{icon_name}.png"
    )


@register.simple_tag
def document_modified_at(document):
    """
    Retourne la date de la version courante.

    Elle est identique dans les modes liste et icône.
    """

    current_version = getattr(
        document,
        "current_version",
        None,
    )

    if current_version is not None:
        return current_version.created_at

    return document.created_at