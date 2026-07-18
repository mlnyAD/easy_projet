

"""
Widgets HTML du Design System Easy Projet.

Ce module contient les widgets Django spécialisés utilisés
par les composants du Design System.

Il ne contient aucune règle métier.
"""

from django import forms


class TelInput(forms.TextInput):
    """
    Widget Django rendu avec un élément HTML <input type="tel">.
    """

    input_type = "tel"