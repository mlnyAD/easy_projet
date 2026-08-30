

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileUploadDefinition:
    """
    Configuration générique d'un champ d'import de fichiers.
    """

    multiple: bool = False

    allowed_extensions: tuple[str, ...] = ()

    allowed_mime_types: tuple[str, ...] = ()

    max_files: int = 1

    max_file_size: int | None = None

    preview: bool = False

    allow_replace: bool = True

    allow_delete: bool = True

    def __post_init__(self) -> None:
        """
        Valide la cohérence de la configuration d'import.
        """

        if not isinstance(self.multiple, bool):
            raise TypeError(
                "La propriété 'multiple' doit être un booléen."
            )

        if not isinstance(self.allowed_extensions, tuple):
            raise TypeError(
                "La propriété 'allowed_extensions' doit être un tuple."
            )

        if not isinstance(self.allowed_mime_types, tuple):
            raise TypeError(
                "La propriété 'allowed_mime_types' doit être un tuple."
            )

        if isinstance(self.max_files, bool) or not isinstance(
            self.max_files,
            int,
        ):
            raise TypeError(
                "La propriété 'max_files' doit être un entier."
            )

        if self.max_files <= 0:
            raise ValueError(
                "La propriété 'max_files' doit être "
                "strictement positive."
            )

        if (
            not self.multiple
            and self.max_files != 1
        ):
            raise ValueError(
                "Un import mono-fichier doit avoir "
                "'max_files=1'."
            )

        if self.max_file_size is not None:
            if (
                isinstance(self.max_file_size, bool)
                or not isinstance(
                    self.max_file_size,
                    int,
                )
            ):
                raise TypeError(
                    "La propriété 'max_file_size' doit "
                    "être un entier ou None."
                )

            if self.max_file_size <= 0:
                raise ValueError(
                    "La propriété 'max_file_size' doit "
                    "être strictement positive."
                )

        if not isinstance(self.preview, bool):
            raise TypeError(
                "La propriété 'preview' doit être un booléen."
            )

        if not isinstance(self.allow_replace, bool):
            raise TypeError(
                "La propriété 'allow_replace' doit être un booléen."
            )

        if not isinstance(self.allow_delete, bool):
            raise TypeError(
                "La propriété 'allow_delete' doit être un booléen."
            )