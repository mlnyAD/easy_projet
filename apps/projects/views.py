

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import DetailView, ListView

from common.constants import (
    DEFAULT_PAGE_SIZE,
    PAGE_SIZE_VALUES,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from .form_definition import PROJECT_FORM_DEFINITION
from .forms import (
    ProjectExternalParticipantFormSet,
    ProjectForm,
    ProjectMembershipFormSet,
)
from .lists import PROJECT_LIST_DEFINITION
from .models import Project
from .services.access import ProjectAccessService
from django.conf import settings
from .services.geocoding import (
    ProjectGeocodingError,
    ProjectGeocodingService,
)
from apps.users.models import User


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            Project.objects
            .select_related(
                "client_environment",
                "client_environment__company",
                "company",
                "owner_company",
                "project_manager",
                "status",
            )
            .order_by(
                "reference",
                "name",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=PROJECT_LIST_DEFINITION,
            rows=django_page.object_list,
        )

        framework_page = ListPage(
            rows=tuple(django_page.object_list),
            page=django_page.number,
            page_size=django_page.paginator.per_page,
            total_items=django_page.paginator.count,
            total_pages=django_page.paginator.num_pages,
            has_previous=django_page.has_previous(),
            has_next=django_page.has_next(),
        )

        list_view = ListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
        )

        context["list_view"] = list_view

        # Alias temporaire pour compatibilité avec les tests existants.
        context["list"] = list_view

        context["page_sizes"] = PAGE_SIZE_VALUES
        context["row_actions_template"] = (
            "projects/project_actions.html"
        )

        return context

class ProjectLocationView(ListView):
    """
    Localisation de tous les projets accessibles.

    Les coordonnées déjà enregistrées sont utilisées directement.
    Les projets sans coordonnées sont géocodés à la demande.
    Les projets impossibles à géolocaliser restent visibles
    dans une liste distincte.
    """

    model = Project
    template_name = "projects/project_location.html"
    context_object_name = "projects"

    def get_queryset(self):
        return (
            ProjectAccessService
            .get_accessible_projects(self.request.user)
            .select_related(
                "company",
                "client_environment",
                "client_environment__company",
            )
        )

    @staticmethod
    def build_project_data(project):
        address_parts = [
            project.address_1,
            project.address_2,
            project.address_3,
            project.postal_code,
            project.city,
            project.country,
        ]

        full_address = ", ".join(
            part.strip()
            for part in address_parts
            if part and part.strip()
        )

        return {
            "id": str(project.pk),
            "reference": project.reference,
            "name": project.name,
            "company": str(project.company),
            "address": full_address,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        localized_projects = []
        unlocalized_projects = []

        for project in context["projects"]:
            project_data = self.build_project_data(project)

            if (
                project.latitude is None
                or project.longitude is None
            ):
                try:
                    coordinates = (
                        ProjectGeocodingService
                        .geocode_and_save(project)
                    )

                except ProjectGeocodingError as exc:
                    project_data["localization_error"] = str(exc)
                    unlocalized_projects.append(project_data)
                    continue

                if coordinates is None:
                    project_data["localization_error"] = (
                        "Adresse non localisable."
                    )
                    unlocalized_projects.append(project_data)
                    continue

            project_data["latitude"] = float(project.latitude)
            project_data["longitude"] = float(project.longitude)

            localized_projects.append(project_data)

        context["projects_data"] = localized_projects
        context["unlocalized_projects"] = unlocalized_projects
        context["google_maps_api_key"] = (
            settings.GOOGLE_MAPS_API_KEY
        )

        return context
        
class ProjectWorkspaceView(DetailView):
    """
    Résumé et point d'entrée fonctionnel d'un projet.

    Cette vue ne permet aucune modification directe des données.
    """

    model = Project
    template_name = "projects/project_workspace.html"
    context_object_name = "project"

    def get_queryset(self):
        return (
            Project.objects
            .select_related(
                "client_environment",
                "client_environment__company",
                "company",
                "owner_company",
                "project_manager",
                "status",
            )
            .prefetch_related(
                "work_packages",
                "work_packages__tasks",
                "memberships",
                "memberships__user",
                "memberships__user__company",
                "memberships__role",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.object

        context["current_project"] = project

        context["work_package_count"] = (
            project.work_packages.count()
        )

        context["task_count"] = sum(
            work_package.tasks.count()
            for work_package in project.work_packages.all()
        )

        # Aucun calcul métier d'avancement n'est encore validé.
        context["progress_percent"] = None

        return context


class ProjectCreateView(EPCreateView):
    model = Project
    form_class = ProjectForm
    definition = PROJECT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("projects:list")
    cancel_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le projet a été créé avec succès.",
        )

        return response


class ProjectUpdateView(EPUpdateView):
    """
    Modification d'un projet et de ses participants.
    """

    model = Project
    form_class = ProjectForm
    definition = PROJECT_FORM_DEFINITION
    template_name = "projects/project_form.html"

    def get_queryset(self):
        return (
            Project.objects
            .select_related(
                "client_environment",
                "client_environment__company",
                "company",
                "owner_company",
                "designer_company",
                "project_manager",
                "status",
                "project_type",
            )
            .prefetch_related(
                "memberships",
                "memberships__user",
                "memberships__user__company",
                "memberships__role",
                "memberships__role__catalog_type",
                "external_participants",
                "external_participants__access_level",
                "external_participants__converted_user",
            )
        )

    def get_return_url(self):
        candidate = self.request.GET.get("next")

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={self.request.get_host()},
                require_https=self.request.is_secure(),
            )
        ):
            return candidate

        return reverse_lazy("projects:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_membership_formset(
        self,
        *,
        data=None,
    ):
        return ProjectMembershipFormSet(
            data=data,
            instance=self.object,
            prefix="memberships",
        )

    def get_external_participant_formset(
        self,
        *,
        data=None,
    ):
        return ProjectExternalParticipantFormSet(
            data=data,
            instance=self.object,
            prefix="external_participants",
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "membership_formset" not in context:
            context["membership_formset"] = (
                self.get_membership_formset()
            )

        if "external_participant_formset" not in context:
            context["external_participant_formset"] = (
                self.get_external_participant_formset()
            )

        users = (
            User.objects
            .filter(is_active=True)
            .select_related(
                "company",
                "global_role",
                "access_level",
            )
            .order_by(
                "last_name",
                "first_name",
            )
        )

        context["project_users_data"] = [
            {
                "id": str(user.pk),
                "last_name": user.last_name,
                "first_name": user.first_name,
                "email": user.email,
                "company": str(user.company),
                "global_role": user.global_role.label,
                "access_level": user.access_level.label,
            }
            for user in users
        ]

        return context
   
    def form_valid(self, form):
        membership_formset = self.get_membership_formset(
            data=self.request.POST,
        )

        external_participant_formset = (
            self.get_external_participant_formset(
                data=self.request.POST,
            )
        )

        memberships_valid = membership_formset.is_valid()

        external_participants_valid = (
            external_participant_formset.is_valid()
        )

        if not (
            memberships_valid
            and external_participants_valid
        ):
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    membership_formset=membership_formset,
                    external_participant_formset=(
                        external_participant_formset
                    ),
                )
            )

        with transaction.atomic():
            self.object = form.save()

            membership_formset.instance = self.object
            membership_formset.save()

            external_participant_formset.instance = self.object
            external_participant_formset.save()

        messages.success(
            self.request,
            "Le projet a été modifié avec succès.",
        )

        return redirect(
            self.get_success_url()
        )