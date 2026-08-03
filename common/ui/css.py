

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
    "disabled:bg-gray-100 "
    "disabled:text-gray-500 "
    "disabled:opacity-100 "
    "read-only:cursor-default "
    "read-only:bg-gray-100 "
    "read-only:text-gray-600 "
    "dark:disabled:bg-neutral-900 "
    "dark:disabled:text-neutral-500 "
    "dark:read-only:bg-neutral-900 "
    "dark:read-only:text-neutral-400"
)

INPUT_NORMAL_CLASSES = (
    "border-gray-300 "
    "bg-[#F4FBFA] "
    "text-gray-900 "
    "focus:border-[#0D5262] "
    "focus:ring-[#0D5262]/20 "
    "dark:border-neutral-700 "
    "dark:bg-neutral-800/70 "
    "dark:text-neutral-100 "
    "dark:focus:border-[#248A8D] "
    "dark:focus:ring-[#248A8D]/20"
)

INPUT_ERROR_CLASSES = (
    "border-red-500 "
    "bg-red-50 "
    "text-gray-900 "
    "focus:border-red-500 "
    "focus:ring-red-500/20 "
    "dark:border-red-500 "
    "dark:bg-red-950/20 "
    "dark:text-neutral-100"
)

# =============================================================================
# Cases à cocher
# =============================================================================

CHECKBOX_CLASSES = (
    "size-7 "
    "shrink-0 "
    "rounded "
    "border-gray-300 "
    "text-[#0D5262] "
    "accent-[#0D5262] "
    "cursor-pointer "
    "transition-colors duration-150 "
    "focus:outline-none "
    "focus:ring-2 "
    "focus:ring-[#0D5262]/20 "
    "focus:ring-offset-1 "
    "disabled:cursor-not-allowed "
    "disabled:opacity-50 "
    "dark:border-neutral-700 "
    "dark:bg-neutral-900"
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
    "disabled:opacity-50"
)

PRIMARY_BUTTON_CLASSES = (
    "bg-axcio-light "
    "hover:bg-axcio-light-hover "
    "text-white "
    "focus:ring-axcio-light"
)

BUTTON_SECONDARY_CLASSES = (
    "bg-gray-300 "
    "text-gray-900 "
    "hover:bg-gray-400 "
    "focus:ring-gray-400 "
    "dark:bg-neutral-700 "
    "dark:text-white "
    "dark:hover:bg-neutral-600"
)

BUTTON_DANGER_CLASSES = (
    "bg-red-600 "
    "text-white "
    "hover:bg-red-700 "
    "focus:ring-red-600 "
    "dark:bg-red-700 "
    "dark:hover:bg-red-800"
)