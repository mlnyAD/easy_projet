

"""
Classes CSS des boutons du Design System Easy Projet.

Ce module ne contient aucune logique métier.
Il associe les intentions fonctionnelles des boutons
à leur représentation graphique.
"""

from __future__ import annotations


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


BUTTON_EXECUTE_CLASSES = (
    "bg-axcio-light "
    "text-white "
    "hover:bg-axcio-light-hover "
    "focus:ring-axcio-light "
    "dark:bg-axcio-light "
    "dark:hover:bg-axcio-light-hover"
)


BUTTON_CANCEL_CLASSES = (
    "border border-gray-300 "
    "bg-white "
    "text-gray-700 "
    "hover:bg-gray-50 "
    "focus:ring-gray-400 "
    "dark:border-neutral-600 "
    "dark:bg-neutral-800 "
    "dark:text-neutral-100 "
    "dark:hover:bg-neutral-700"
)


BUTTON_DANGER_CLASSES = (
    "bg-red-600 "
    "text-white "
    "hover:bg-red-700 "
    "focus:ring-red-600 "
    "dark:bg-red-700 "
    "dark:hover:bg-red-800"
)