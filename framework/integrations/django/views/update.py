

"""
Vue générique de modification Easy Projet.
"""

from django.core.exceptions import PermissionDenied
from django.views.generic import UpdateView

from framework.form import FormMode

from .form import EPFormView


class EPUpdateView(
    EPFormView,
    UpdateView,
):
    """
    Vue générique de modification.

    Une vue métier peut surcharger can_edit_object() pour
    ouvrir l'objet en lecture seule lorsque l'utilisateur
    possède un droit de consultation, mais pas de modification.
    """

    def can_edit_object(self) -> bool:
        """
        Indique si l'utilisateur peut modifier l'objet courant.

        Par défaut, une vue de modification reste éditable.
        """

        return True

    def get_form_mode(self):
        """
        Retourne le mode du formulaire courant.
        """

        if self.can_edit_object():
            return FormMode.EDIT

        return FormMode.READONLY

    def get_form(
        self,
        form_class=None,
    ):
        """
        Désactive tous les champs Django en lecture seule.
        """

        form = super().get_form(
            form_class=form_class,
        )

        if self.get_form_mode() is FormMode.READONLY:
            for field in form.fields.values():
                field.disabled = True

        return form

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Interdit toute écriture sur un objet ouvert en lecture seule.
        """

        self.object = self.get_object()

        if self.get_form_mode() is FormMode.READONLY:
            raise PermissionDenied(
                "Vous ne pouvez pas modifier cet élément."
            )

        return super().post(
            request,
            *args,
            **kwargs,
        )