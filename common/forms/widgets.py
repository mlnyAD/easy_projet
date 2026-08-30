

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


class FileUploadInput(forms.ClearableFileInput):
    """
    Widget fichier utilisé par le composant FileUpload EDF.

    Le comportement de ClearableFileInput est conservé afin
    de bénéficier notamment de la gestion Django de la
    suppression d'un fichier existant.

    En revanche, le rendu HTML natif
    "Currently / Clear / Change" n'est pas utilisé :
    le composant FileUpload EDF prend en charge cette
    présentation.
    """

    template_name = "django/forms/widgets/input.html"