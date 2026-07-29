

"""
Rendu des champs du framework Easy Projet.
"""

from django.forms.boundfield import BoundField
from django.forms.widgets import (
    CheckboxInput,
    DateInput,
    Select,
    Textarea,
)
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

    WIDGET_TEMPLATE = {
        Textarea: "edf/form/fields/textarea.html",
        Select: "edf/form/fields/select.html",
        CheckboxInput: "edf/form/fields/checkbox.html",
        DateInput: "edf/form/fields/date.html",
    }

    def get_template_name(self, field):

        if isinstance(field, FieldDefinition):
            return self.TEMPLATE_BY_KIND.get(
                field.kind,
                self.DEFAULT_TEMPLATE,
            )

        if isinstance(field, BoundField):

            widget = field.field.widget

            for widget_type, template in self.WIDGET_TEMPLATE.items():
                if isinstance(widget, widget_type):
                    return template

            return "edf/form/fields/text.html"

        return self.DEFAULT_TEMPLATE