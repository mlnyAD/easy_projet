

from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

from apps.projects.models import Project
from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from .form_definition import RISK_FORM_DEFINITION
from .forms import RiskForm
from .lists import RISK_LIST_DEFINITION
from .models import Risk


class RiskListView(
    EPListPaginationMixin,
    ListView,
):
    """
    Liste globale des risques et opportunités.
    """

    model = Risk
    template_name = "risks/risk_list.html"
    context_object_name = "risks"

    def get_queryset(self):
        return (
            Risk.objects
            .select_related(
                "project",
                "owner",
                "origin",
                "risk_type",
                "risk_class",
                "impact",
                "severity",
                "probability",
                "status",
                "criticality",
                "review_frequency",
            )
            .order_by(
                "project__reference",
                "reference",
                "title",
            )
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def get_return_url(self) -> str:
        """
        Retourne l'écran vers lequel revenir après une création
        ou une modification.
        """

        return self.request.get_full_path()

    def get_create_project(self) -> Project | None:
        """
        Retourne le projet à présélectionner lors de la création.

        La liste globale n'impose aucun projet.
        """

        return None

    def get_create_url(self) -> str:
        """
        Construit l'URL de création d'un risque.

        Les paramètres de navigation sont préparés par la vue afin
        que le template reste indépendant des règles de navigation.
        """

        parameters = {
            "next": self.get_return_url(),
        }

        project = self.get_create_project()

        if project is not None:
            parameters["project"] = str(
                project.pk
            )

        return (
            f"{reverse('risks:create')}?"
            f"{urlencode(parameters)}"
        )

    # ------------------------------------------------------------------
    # Présentation
    # ------------------------------------------------------------------

    def get_page_title(self) -> str:
        """
        Retourne le titre de la page.
        """

        return "Risques"

    def get_page_subtitle(self) -> str:
        """
        Retourne le sous-titre facultatif de la page.
        """

        return ""

    # ------------------------------------------------------------------
    # Contexte
    # ------------------------------------------------------------------

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )

        django_page = context[
            "page_obj"
        ]

        runtime = EPList(
            definition=RISK_LIST_DEFINITION,
            rows=django_page.object_list,
        )

        framework_page = ListPage(
            rows=tuple(
                django_page.object_list
            ),
            page=django_page.number,
            page_size=(
                django_page.paginator.per_page
            ),
            total_items=(
                django_page.paginator.count
            ),
            total_pages=(
                django_page.paginator.num_pages
            ),
            has_previous=(
                django_page.has_previous()
            ),
            has_next=(
                django_page.has_next()
            ),
        )

        list_view = (
            ListViewModelBuilder()
            .build(
                runtime=runtime,
                page=framework_page,
            )
        )

        context["list_view"] = list_view

        # Alias temporaire pour compatibilité
        # avec les tests existants.
        context["list"] = list_view

        context["row_actions_template"] = (
            "risks/risk_actions.html"
        )

        context["is_project_context"] = False

        # Navigation
        context["return_url"] = (
            self.get_return_url()
        )

        context["page_action_url"] = (
            self.get_create_url()
        )

        # Page EDF
        context["page_title"] = (
            self.get_page_title()
        )

        context["page_subtitle"] = (
            self.get_page_subtitle()
        )

        return context


class RiskListByProjectView(RiskListView):
    """
    Liste des risques et opportunités d'un projet donné.
    """

    def get_project(self) -> Project:
        if not hasattr(
            self,
            "_project",
        ):
            self._project = (
                get_object_or_404(
                    Project.objects.select_related(
                        "owner_company",
                        "project_manager",
                        "status",
                    ),
                    pk=self.kwargs[
                        "project_pk"
                    ],
                )
            )

        return self._project

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                project=self.get_project(),
            )
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def get_return_url(self) -> str:
        """
        Depuis le contexte projet, la création ou modification
        revient au résumé du projet.
        """

        project = self.get_project()

        return reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )

    def get_create_project(self) -> Project:
        """
        Présélectionne le projet courant lors de la création.
        """

        return self.get_project()

    # ------------------------------------------------------------------
    # Présentation
    # ------------------------------------------------------------------

    def get_page_title(self) -> str:
        return "Risques du projet"

    def get_page_subtitle(self) -> str:
        project = self.get_project()

        return (
            f"{project.reference} "
            f"— {project.name}"
        )

    # ------------------------------------------------------------------
    # Contexte
    # ------------------------------------------------------------------

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )

        project = self.get_project()

        context["project"] = project
        context["current_project"] = project
        context["is_project_context"] = True

        return context


class RiskCreateView(EPCreateView):
    model = Risk
    form_class = RiskForm
    definition = RISK_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_return_url(self):
        candidate = self.request.GET.get(
            "next"
        )

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    self.request.get_host()
                },
                require_https=(
                    self.request.is_secure()
                ),
            )
        ):
            return candidate

        return reverse_lazy(
            "risks:list"
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_initial(self):
        initial = super().get_initial()

        project_pk = self.request.GET.get(
            "project"
        )

        if project_pk:
            project = (
                Project.objects
                .filter(
                    pk=project_pk,
                    is_active=True,
                )
                .first()
            )

            if project is not None:
                initial["project"] = project

        return initial

    def form_valid(self, form):
        response = super().form_valid(
            form
        )

        messages.success(
            self.request,
            "Le risque a été créé avec succès.",
        )

        return response


class RiskUpdateView(EPUpdateView):
    model = Risk
    form_class = RiskForm
    definition = RISK_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_return_url(self):
        candidate = self.request.GET.get(
            "next"
        )

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    self.request.get_host()
                },
                require_https=(
                    self.request.is_secure()
                ),
            )
        ):
            return candidate

        return reverse_lazy(
            "risks:list"
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(
            form
        )

        messages.success(
            self.request,
            "Le risque a été modifié avec succès.",
        )

        return response