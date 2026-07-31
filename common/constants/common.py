

"""
Constantes techniques communes à Easy Projet.

Ce module ne contient que des constantes indépendantes du métier.
Les constantes propres à une entité restent dans les modules dédiés
(company.py, catalog.py, user.py, etc.).
"""

# ============================================================================
# Longueurs génériques
# ============================================================================

CODE_LENGTH = 30
SHORT_LABEL_LENGTH = 50
LABEL_LENGTH = 100
NAME_LENGTH = 100
TITLE_LENGTH = 150

EMAIL_LENGTH = 254
PHONE_LENGTH = 20
URL_LENGTH = 500

ADDRESS_LENGTH = 150
POSTAL_CODE_LENGTH = 20
CITY_LENGTH = 100
COUNTRY_LENGTH = 100

SHORT_TEXT_LENGTH = 255

# ============================================================================
# Pagination
# ============================================================================

DEFAULT_PAGE_SIZE = 20

PAGE_SIZE_VALUES = (10, 20, 50, 100)

PAGE_SIZE_CHOICES = tuple(
    (value, str(value))
    for value in PAGE_SIZE_VALUES
)

# ============================================================================
# Formats d'affichage
# ============================================================================

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"