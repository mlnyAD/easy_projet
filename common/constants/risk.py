

"""
Constantes de l'entité Risk.
"""

from common.constants.common import (
    CODE_LENGTH,
    TITLE_LENGTH,
)


# ============================================================================
# Longueurs
# ============================================================================

RISK_REFERENCE_LENGTH = CODE_LENGTH
RISK_TITLE_LENGTH = TITLE_LENGTH
RISK_DESCRIPTION_LENGTH = 2000
RISK_PLANNED_ACTIONS_LENGTH = 2000


# ============================================================================
# Montants
# ============================================================================

RISK_ESTIMATED_COST_MAX_DIGITS = 14
RISK_ESTIMATED_COST_DECIMAL_PLACES = 2


# ============================================================================
# Génération des références
# ============================================================================

RISK_REFERENCE_PREFIX = "RSK"
RISK_REFERENCE_SEQUENCE_DIGITS = 3