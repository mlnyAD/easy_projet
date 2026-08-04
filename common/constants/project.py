

"""
Constantes de l'entité Project.
"""

from decimal import Decimal

from .common import (
    ADDRESS_LENGTH,
    CITY_LENGTH,
    COUNTRY_LENGTH,
    POSTAL_CODE_LENGTH,
)

# ------------------------------------------------------------------
# Identification
# ------------------------------------------------------------------

PROJECT_REFERENCE_LENGTH = 50
PROJECT_NAME_LENGTH = 150

# Descriptions et commentaires
PROJECT_DESCRIPTION_LENGTH = 2000
PROJECT_CONTRACT_REFERENCE_LENGTH = 100
PROJECT_COMMENT_LENGTH = 4000

# ------------------------------------------------------------------
# Localisation
# ------------------------------------------------------------------

PROJECT_ADDRESS_LENGTH = ADDRESS_LENGTH
PROJECT_POSTAL_CODE_LENGTH = POSTAL_CODE_LENGTH
PROJECT_CITY_LENGTH = CITY_LENGTH
PROJECT_COUNTRY_LENGTH = COUNTRY_LENGTH

# ------------------------------------------------------------------
# Charge
# ------------------------------------------------------------------

PROJECT_DEFAULT_WORKLOAD_HOURS = 0

# ------------------------------------------------------------------
# Financier (vision commerciale)
# ------------------------------------------------------------------

PROJECT_CURRENCY_LENGTH = 3
PROJECT_DEFAULT_CURRENCY = "EUR"

PROJECT_AMOUNT_MAX_DIGITS = 14
PROJECT_AMOUNT_DECIMAL_PLACES = 2
PROJECT_DEFAULT_AMOUNT = Decimal("0.00")