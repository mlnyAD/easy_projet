

"""
Constantes du domaine documentaire.
"""

from common.constants.common import (
    NAME_LENGTH,
    SHORT_TEXT_LENGTH,
)

# ----------------------------------------------------------------------
# Dossiers
# ----------------------------------------------------------------------

DOCUMENT_FOLDER_NAME_LENGTH = NAME_LENGTH

# ----------------------------------------------------------------------
# Documents
# ----------------------------------------------------------------------

DOCUMENT_TITLE_LENGTH = 255

# ----------------------------------------------------------------------
# Versions
# ----------------------------------------------------------------------

DOCUMENT_FILENAME_LENGTH = 255
DOCUMENT_STORAGE_KEY_LENGTH = 500
DOCUMENT_MIME_TYPE_LENGTH = 150
DOCUMENT_CHECKSUM_LENGTH = 64

# SHA-256
DOCUMENT_CHECKSUM_ALGORITHM = "sha256"

# ----------------------------------------------------------------------
# Historique
# ----------------------------------------------------------------------

DOCUMENT_HISTORY_ACTION_LENGTH = 40
DOCUMENT_HISTORY_DETAILS_LENGTH = 2000