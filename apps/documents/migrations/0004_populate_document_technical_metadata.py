from pathlib import Path

from django.db import migrations


CAD_EXTENSIONS = frozenset(
    {
        ".dwg",
        ".dxf",
        ".dwf",
        ".dgn",
        ".pcf",
    }
)

OFFICE_EXTENSIONS = frozenset(
    {
        ".docx",
        ".xlsx",
        ".pptx",
    }
)

IMAGE_EXTENSIONS = frozenset(
    {
        ".bmp",
        ".gif",
        ".jpeg",
        ".jpg",
        ".png",
        ".tif",
        ".tiff",
        ".webp",
    }
)

MEDIA_EXTENSIONS = frozenset(
    {
        ".avi",
        ".m4a",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".ogg",
        ".wav",
        ".webm",
    }
)


def detect_technical_type(
    *,
    extension,
    mime_type,
):
    normalized_extension = (
        extension
        .strip()
        .lower()
    )

    normalized_mime_type = (
        (mime_type or "")
        .strip()
        .lower()
    )

    if normalized_extension in CAD_EXTENSIONS:
        return "CAD"

    if normalized_extension in OFFICE_EXTENSIONS:
        return "OFFICE"

    if normalized_extension == ".pdf":
        return "PDF"

    if (
        normalized_extension in IMAGE_EXTENSIONS
        or normalized_mime_type.startswith("image/")
    ):
        return "IMAGE"

    if (
        normalized_extension in MEDIA_EXTENSIONS
        or normalized_mime_type.startswith("audio/")
        or normalized_mime_type.startswith("video/")
    ):
        return "MEDIA"

    return "OTHER"


def populate_technical_metadata(
    apps,
    schema_editor,
):
    DocumentVersion = apps.get_model(
        "documents",
        "DocumentVersion",
    )

    for version in DocumentVersion.objects.all().iterator():
        extension = (
            Path(version.original_filename)
            .suffix
            .lower()
        )

        technical_type = detect_technical_type(
            extension=extension,
            mime_type=version.mime_type,
        )

        DocumentVersion.objects.filter(
            pk=version.pk,
        ).update(
            extension=extension,
            technical_type=technical_type,
        )


def clear_technical_metadata(
    apps,
    schema_editor,
):
    DocumentVersion = apps.get_model(
        "documents",
        "DocumentVersion",
    )

    DocumentVersion.objects.all().update(
        extension="",
        technical_type="",
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "documents",
            "0003_documentversion_extension_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            populate_technical_metadata,
            clear_technical_metadata,
        ),
    ]