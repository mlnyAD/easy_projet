

"""
Constantes de l'entité Meeting.
"""

from common.constants.common import (
    CODE_LENGTH,
    SHORT_TEXT_LENGTH,
    TITLE_LENGTH,
)


# ============================================================================
# Référence
# ============================================================================

MEETING_REFERENCE_LENGTH = CODE_LENGTH
MEETING_REFERENCE_PREFIX = "MTG"
MEETING_REFERENCE_SEQUENCE_DIGITS = 3


# ============================================================================
# Libellés et textes
# ============================================================================

MEETING_SUBJECT_LENGTH = TITLE_LENGTH
MEETING_LOCATION_LENGTH = SHORT_TEXT_LENGTH
MEETING_COMMENTS_LENGTH = 2000


# ============================================================================
# Durée
# ============================================================================

MEETING_DURATION_MAX_DIGITS = 5
MEETING_DURATION_DECIMAL_PLACES = 2
MEETING_DURATION_MAX_HOURS = 999.99


# ============================================================================
# Participant externe
# ============================================================================

MEETING_PARTICIPANT_EXTERNAL_NAME_LENGTH = 150
MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH = 254