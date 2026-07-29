

"""
Adaptation des widgets Django au Design System Easy Projet.
"""

from django.forms import Widget


class WidgetAdapter:
    """
    Adapte un widget Django aux conventions Easy Projet.
    """

    DEFAULT_INPUT_CLASS = "edf-form-input"

    def adapt(self, widget: Widget) -> Widget:
        """
        Applique les conventions Easy Projet au widget.
        """

        css_classes = widget.attrs.get("class", "").split()

        if self.DEFAULT_INPUT_CLASS not in css_classes:
            css_classes.append(self.DEFAULT_INPUT_CLASS)

        widget.attrs["class"] = " ".join(css_classes)

        return widget