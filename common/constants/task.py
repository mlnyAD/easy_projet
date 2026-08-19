

"""
Constantes de l'entité Task.
"""

from common.constants.common import (
    CODE_LENGTH,
    NAME_LENGTH,
)

# ----------------------------------------------------------------------
# Longueurs
# ----------------------------------------------------------------------

TASK_CODE_LENGTH = CODE_LENGTH
TASK_NAME_LENGTH = NAME_LENGTH
TASK_DESCRIPTION_LENGTH = 2000

# ----------------------------------------------------------------------
# Charges
# ----------------------------------------------------------------------

TASK_DEFAULT_PLANNED_WORKLOAD_HOURS = 0
TASK_DEFAULT_REMAINING_WORKLOAD_HOURS = 0

# ----------------------------------------------------------------------
# Avancement
# ----------------------------------------------------------------------

TASK_DEFAULT_PROGRESS_PERCENT = 0
TASK_MIN_PROGRESS_PERCENT = 0
TASK_MAX_PROGRESS_PERCENT = 100

# ----------------------------------------------------------------------
# Affectation des ressources
# ----------------------------------------------------------------------

TASK_ASSIGNMENT_DEFAULT_ALLOCATION_PERCENT = 100
TASK_ASSIGNMENT_MIN_ALLOCATION_PERCENT = 0
TASK_ASSIGNMENT_MAX_ALLOCATION_PERCENT = 100