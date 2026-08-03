

"""
common/ui/css.py

Constantes CSS utilisées par les composants du Design System Easy Projet.
Aucune logique métier ne doit apparaître dans ce fichier.
"""

from __future__ import annotations


# =============================================================================
# Listes
# =============================================================================

COLUMN_WIDTH_CLASSES = {
    "auto": "",
    "xs": "w-20 max-w-20",
    "s": "w-24 max-w-24",
    "sm": "w-32 max-w-32",
    "md": "w-48 max-w-48",
    "lg": "w-64 max-w-64",
    "xl": "w-80 max-w-80",
}

COLUMN_ALIGNMENT_CLASSES = {
    "left": "text-left",
    "center": "text-center",
    "right": "text-right",
}


# =============================================================================
# Couleurs Easy Projet
# =============================================================================

PRIMARY_COLOR = "#248A8D"


# =============================================================================
# Champs de saisie
# =============================================================================

INPUT_BASE_CLASSES = (
    "block w-full rounded-lg border "
    "px-3 py-2 "
    "text-sm shadow-sm transition "
    "focus:outline-none focus:ring-2 "
    "disabled:cursor-not-allowed "
    "disabled:bg-axcio-input-disabled "
    "disabled:text-axcio-text-muted "
    "disabled:opacity-100 "
    "read-only:cursor-default "
    "read-only:bg-axcio-input-disabled "
    "read-only:text-axcio-text-secondary "
    "dark:disabled:bg-axcio-input-disabled-dark "
    "dark:disabled:text-axcio-text-muted-dark "
    "dark:read-only:bg-axcio-input-disabled-dark "
    "dark:read-only:text-axcio-text-muted-dark"
)

INPUT_NORMAL_CLASSES = (
    "border-axcio-border "
    "bg-axcio-input "
    "text-axcio-text "
    "focus:border-axcio-dark "
    "focus:ring-axcio-dark/20 "
    "dark:border-axcio-border-dark "
    "dark:bg-axcio-input-dark "
    "dark:text-axcio-text-dark "
    "dark:focus:border-axcio-light "
    "dark:focus:ring-axcio-light/20"
)

INPUT_ERROR_CLASSES = (
    "border-axcio-danger "
    "bg-axcio-danger-soft "
    "text-axcio-text "
    "focus:border-axcio-danger "
    "focus:ring-axcio-danger/20 "
    "dark:border-axcio-danger "
    "dark:bg-axcio-danger-soft-dark "
    "dark:text-axcio-text-dark"
)


# =============================================================================
# Cases à cocher
# =============================================================================

CHECKBOX_CLASSES = (
    "size-7 "
    "shrink-0 "
    "rounded "
    "border-axcio-border "
    "bg-axcio-input "
    "text-axcio-dark "
    "accent-axcio-dark "
    "cursor-pointer "
    "transition-colors duration-150 "
    "focus:outline-none "
    "focus:ring-2 "
    "focus:ring-axcio-dark/20 "
    "focus:ring-offset-1 "
    "disabled:cursor-not-allowed "
    "disabled:opacity-50 "
    "dark:border-axcio-border-dark "
    "dark:bg-axcio-input-dark "
    "dark:text-axcio-light "
    "dark:accent-axcio-light "
    "dark:focus:ring-axcio-light/20 "
    "dark:focus:ring-offset-axcio-page-dark"
)


# =============================================================================
# Boutons
# =============================================================================

BUTTON_BASE_CLASSES = (
    "inline-flex items-center justify-center "
    "rounded-lg "
    "px-4 py-2 "
    "text-sm font-medium "
    "transition-colors duration-200 "
    "focus:outline-none "
    "focus:ring-2 "
    "focus:ring-offset-2 "
    "disabled:cursor-not-allowed "
    "disabled:opacity-50 "
    "dark:focus:ring-offset-axcio-page-dark"
)

PRIMARY_BUTTON_CLASSES = (
    "bg-axcio-light "
    "text-white "
    "hover:bg-axcio-light-hover "
    "focus:ring-axcio-light"
)

BUTTON_SECONDARY_CLASSES = (
    "border border-axcio-border "
    "bg-axcio-surface-alt "
    "text-axcio-text-secondary "
    "hover:bg-axcio-border-light "
    "focus:ring-axcio-border "
    "dark:border-axcio-border-dark "
    "dark:bg-axcio-surface-alt-dark "
    "dark:text-axcio-text-secondary-dark "
    "dark:hover:bg-axcio-border-dark "
    "dark:focus:ring-axcio-border-dark"
)

BUTTON_DANGER_CLASSES = (
    "bg-axcio-danger "
    "text-white "
    "hover:bg-red-700 "
    "focus:ring-axcio-danger "
    "dark:bg-axcio-danger "
    "dark:hover:bg-red-700"
)