

"""
Vue de base des formulaires Easy Projet.
"""

from framework.form import EPForm
from framework.integrations.django.form_renderer import DjangoFormRenderer

from .base import EPViewMixin


class EPFormView(EPViewMixin):
    """
    Comportement commun à toutes les vues de formulaire.
    """

    definition = None
    renderer_class = DjangoFormRenderer

    def get_form_mode(self):
        """
        Retourne le mode du formulaire.

        Cette méthode est spécialisée par les classes dérivées.
        """
        raise NotImplementedError

    def get_formsets(
        self,
        *,
        django_form,
        context,
    ) -> dict:
        """
        Retourne les formsets associés au formulaire.

        Par défaut, un formulaire Easy Projet ne possède
        aucune collection répétable.

        Les vues spécialisées peuvent surcharger cette méthode
        pour fournir les formsets correspondant aux collections
        déclarées dans FormDefinition.
        """
        return {}

    def get_ep_form(
        self,
        django_form,
        *,
        formsets=None,
    ) -> EPForm:
        """
        Construit le formulaire Easy Projet.
        """
        return EPForm(
            definition=self.definition,
            context=self.get_ep_context(),
            providers=self.get_provider_registry(),
            mode=self.get_form_mode(),
            django_form=django_form,
            formsets=formsets or {},
        )

    def get_renderer(self):
        return self.renderer_class()

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(**kwargs)

        django_form = context["form"]

        formsets = self.get_formsets(
            django_form=django_form,
            context=context,
        )

        ep_form = self.get_ep_form(
            django_form,
            formsets=formsets,
        )

        renderer = self.get_renderer()

        return renderer.build_context(
            ep_form,
            cancel_url=self.get_cancel_url(),
            context=context,
        )