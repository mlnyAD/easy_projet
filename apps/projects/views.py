

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.generic import (
    DetailView,
    ListView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta
from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from django.db.models import Sum

from apps.tasks.models import Task, TaskAssignment

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
    ProjectPhotoForm,
)
from .lists import PROJECT_LIST_DEFINITION
from .models import Project
from .services.access import ProjectAccessService
from django.conf import settings
from .services.geocoding import (
    ProjectGeocodingError,
    ProjectGeocodingService,
)


class ProjectListView(
    EPListPaginationMixin,
    ListView,
):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return (
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
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
            rows=tuple(
                django_page.object_list
            ),
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
        queryset = (
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            )
            .select_related(
                "company",
                "client_environment",
                "client_environment__company",
            )
        )

        project_id = (
            self.request.GET
            .get("project")
        )

        if project_id:
            queryset = queryset.filter(
                pk=project_id
            )

        return queryset

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

class ProjectFormCollectionsMixin:
    """
    Gestion générique des collections du formulaire Projet.
    """

    success_message = None

    def get_return_url(self):
        candidate = self.request.GET.get("next")

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

        return reverse("projects:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_membership_formset(
        self,
        *,
        data=None,
        instance=None,
    ):
        return ProjectMembershipFormSet(
            data=data,
            instance=instance,
            prefix="memberships",
        )

    def get_external_participant_formset(
        self,
        *,
        data=None,
        instance=None,
    ):
        return ProjectExternalParticipantFormSet(
            data=data,
            instance=instance,
            prefix="external_participants",
        )

    def get_formsets(
        self,
        *,
        django_form,
        context,
    ):
        if "formsets" in context:
            return context["formsets"]

        instance = django_form.instance

        data = (
            self.request.POST
            if self.request.method == "POST"
            else None
        )

        return {
            "memberships": (
                self.get_membership_formset(
                    data=data,
                    instance=instance,
                )
            ),
            "external_participants": (
                self.get_external_participant_formset(
                    data=data,
                    instance=instance,
                )
            ),
        }

    def form_valid(self, form):
        membership_formset = (
            self.get_membership_formset(
                data=self.request.POST,
                instance=form.instance,
            )
        )

        external_participant_formset = (
            self.get_external_participant_formset(
                data=self.request.POST,
                instance=form.instance,
            )
        )

        memberships_valid = (
            membership_formset.is_valid()
        )

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
                    formsets={
                        "memberships": (
                            membership_formset
                        ),
                        "external_participants": (
                            external_participant_formset
                        ),
                    },
                )
            )

        with transaction.atomic():
            self.object = form.save()

            membership_formset.instance = (
                self.object
            )
            membership_formset.save()

            external_participant_formset.instance = (
                self.object
            )
            external_participant_formset.save()

        if self.success_message:
            messages.success(
                self.request,
                self.success_message,
            )

        return redirect(
            self.get_success_url()
        )

class ProjectCreateView(
    ProjectFormCollectionsMixin,
    EPCreateView,
):
    model = Project
    form_class = ProjectForm
    definition = PROJECT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = (
        "Le projet a été créé avec succès."
    )


class ProjectUpdateView(
    ProjectFormCollectionsMixin,
    EPUpdateView,
):
    """
    Modification d'un projet et de ses participants.
    """

    model = Project
    form_class = ProjectForm
    definition = PROJECT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = (
        "Le projet a été modifié avec succès."
    )

    def get_queryset(self):
        queryset = (
            ProjectAccessService
            .get_accessible_projects(
                self.request.user
            )
            .select_related(
                "company",
                "client_environment",
                "client_environment__company",
            )
        )

        project_id = (
            self.request.GET
            .get("project")
        )

        if project_id:
            queryset = queryset.filter(
                pk=project_id
            )

        return queryset
    
            
class ProjectPhotoUpdateView(
    LoginRequiredMixin,
    UpdateView,
):
    """
    Ajoute ou remplace la photo principale d'un projet.
    """

    model = Project
    form_class = ProjectPhotoForm
    template_name = "projects/project_photo_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "projects:workspace",
            kwargs={
                "pk": self.object.pk,
            },
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            "La photo du projet a été mise à jour.",
        )

        return super().form_valid(form)
    

class ProjectDashboardView(DetailView):
    """
    Tableau de bord synthétique d'un projet.

    Les widgets sont volontairement séparés du template principal
    afin de permettre une future personnalisation du dashboard.
    """

    model = Project
    template_name = "projects/project_dashboard.html"
    context_object_name = "project"

    def get_queryset(self):
        return (
            Project.objects
            .select_related(
                "company",
                "owner_company",
                "project_manager",
                "status",
                "project_type",
                "client_environment",
            )
            .prefetch_related(
                "work_packages",
                "work_packages__tasks",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.object

        context["current_project"] = project

        open_risks = (
            project.risks
            .filter(
                is_active=True,
                status__code__in=(
                    "LATENT",
                    "EMERGED",
                    "ACTIVE",
                ),
                status__catalog_type__code="RISK_STATE",
            )
            .select_related(
                "criticality",
                "status",
            )
            .order_by(
                "-criticality__sort_order",
                "reference",
            )
        )

        context["dashboard_risks"] = open_risks

        context["dashboard_risk_count"] = (
            open_risks.count()
        )

        context["dashboard_major_risk_count"] = (
            open_risks
            .filter(
                criticality__code__in=(
                    "HIGH",
                    "CRITICAL",
                ),
                criticality__catalog_type__code=(
                    "RISK_CRITICALITY"
                ),
            )
            .count()
        )
        
        upcoming_meetings = (
            project.meetings
            .filter(
                is_active=True,
                scheduled_at__gte=timezone.now(),
            )
            .select_related(
                "status",
                "organizer",
            )
            .order_by(
                "scheduled_at",
            )
        )

        context["dashboard_meeting_count"] = (
            upcoming_meetings.count()
        )

        context["dashboard_next_meeting"] = (
            upcoming_meetings.first()
        )
        
        today = timezone.localdate()

        week_start = today - timedelta(
            days=today.weekday()
        )

        week_end = week_start + timedelta(
            days=6
        )

        weekly_tasks = (
            Task.objects
            .filter(
                work_package__project=project,
                is_active=True,
                start_date__lte=week_end,
                end_date__gte=week_start,
            )
        )

        context["dashboard_weekly_task_count"] = (
            weekly_tasks.count()
        )

        context["dashboard_weekly_workload"] = (
            weekly_tasks.aggregate(
                total=Sum("planned_workload_hours")
            )["total"]
            or 0
        )

        context["dashboard_weekly_resource_count"] = (
            TaskAssignment.objects
            .filter(
                task__in=weekly_tasks,
                is_active=True,
            )
            .values("user_id")
            .distinct()
            .count()
        )

        return context