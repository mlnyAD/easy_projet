

"""
Rendu des champs du framework Easy Projet.
"""

from framework.form import FieldDefinition
from framework.form import FieldKind


class FieldRenderer:
    """
    Résout le template associé à un champ.
    """

    DEFAULT_TEMPLATE = "edf/form/field.html"

    TEMPLATE_BY_KIND = {
        FieldKind.TEXT: "edf/form/fields/text.html",
    }

    def get_template_name(self, field):
            return self.TEMPLATE_BY_KIND.get(
                field.kind,
                self.DEFAULT_TEMPLATE,
            )