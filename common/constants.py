

"""
Constantes techniques communes à Easy Projet.

Ce module ne doit contenir que des constantes indépendantes du métier.
Les constantes métier (statuts, types, profils, etc.) appartiennent aux
applications concernées ou aux catalogues.
"""

# ============================================================================
# Longueur des champs
# ============================================================================

CODE_LENGTH = 30
SHORT_LABEL_LENGTH = 50
LABEL_LENGTH = 100
NAME_LENGTH = 100
TITLE_LENGTH = 150

EMAIL_LENGTH = 254          # RFC 5321 / Django
PHONE_LENGTH = 20
URL_LENGTH = 500

SHORT_TEXT_LENGTH = 255

# ============================================================================
# Pagination
# ============================================================================

DEFAULT_PAGE_SIZE = 20
PAGE_SIZE_CHOICES = (10, 20, 50, 100)

# ============================================================================
# Formats d'affichage
# ============================================================================

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"