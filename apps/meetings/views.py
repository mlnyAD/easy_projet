

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView
from urllib.parse import urlencode

from apps.projects.models import Project
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

from .form_definition import MEETING_FORM_DEFINITION
from .forms import (
    ExternalMeetingParticipantFormSet,
    InternalMeetingParticipantFormSet,
    MeetingForm,
)
from .lists import MEETING_LIST_DEFINITION
from .models import Meeting


def get_allowed_return_url(
    request,
    *,
    default_url,
):
    candidate = request.GET.get("next")

    if (
        candidate
        and url_has_allowed_host_and_scheme(
            candidate,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
    ):
        return candidate

    return default_url


class MeetingListView(ListView):
    """
    Liste globale des réunions.
    """

    model = Meeting
    template_name = "meetings/meeting_list.html"
    context_object_name = "meetings"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            Meeting.objects
            .select_related(
                "project",
                "organizer",
                "status",
            )
            .order_by(
                "scheduled_at",
                "project__reference",
                "reference",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=MEETING_LIST_DEFINITION,
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
        context["list"] = list_view
        context["page_sizes"] = PAGE_SIZE_VALUES
        context["row_actions_template"] = (
            "meetings/meeting_actions.html"
        )

        context["is_project_context"] = False
        context["return_url"] = self.request.get_full_path()
        context["current_list_url"] = (
            self.request.get_full_path()
        )

        context["page_title"] = "Réunions"
        context["page_subtitle"] = None
        context["page_back_url"] = None
        context["page_back_label"] = None

        context["page_action_label"] = "Nouvelle réunion"
        context["page_action_icon"] = "plus"

        context["page_action_url"] = (
            f"{reverse('meetings:create')}?"
            f"{urlencode({'next': self.request.get_full_path()})}"
        )

        return context


class MeetingListByProjectView(MeetingListView):
    """
    Liste des réunions d'un projet.
    """

    def get_project(self) -> Project:
        if not hasattr(self, "_project"):
            self._project = get_object_or_404(
                Project.objects.select_related(
                    "owner_company",
                    "project_manager",
                    "status",
                ),
                pk=self.kwargs["project_pk"],
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()

        context["project"] = project
        context["current_project"] = project
        context["is_project_context"] = True

        context["return_url"] = reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )

        context["current_list_url"] = (
            self.request.get_full_path()
        )

        context["page_title"] = "Réunions du projet"

        context["page_subtitle"] = (
            f"{project.reference} — {project.name}"
        )

        context["page_back_url"] = reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )
        context["page_back_label"] = "Retour au projet"

        context["page_action_url"] = (
            f"{reverse('meetings:create')}?"
            f"{urlencode({
                'next': context['return_url'],
                'project': project.pk,
            })}"
        )

        return context


class MeetingCompositeFormMixin:
    """
    Gestion commune du formulaire Réunion + Participants.
    """

    success_message = None

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse("meetings:list"),
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_internal_formset(
        self,
        *,
        data=None,
        instance=None,
    ):
        if instance is None:
            instance = self.object

        return InternalMeetingParticipantFormSet(
            data=data,
            instance=instance,
            prefix="internal",
        )

    def get_external_formset(
        self,
        *,
        data=None,
        instance=None,
    ):
        if instance is None:
            instance = self.object

        return ExternalMeetingParticipantFormSet(
            data=data,
            instance=instance,
            prefix="external",
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
            "internal": self.get_internal_formset(
                data=data,
                instance=instance,
            ),
            "external": self.get_external_formset(
                data=data,
                instance=instance,
            ),
        }
        
    def form_valid(self, form):
        instance = form.instance

        internal_formset = self.get_internal_formset(
            data=self.request.POST,
            instance=instance,
        )
        external_formset = self.get_external_formset(
            data=self.request.POST,
            instance=instance,
        )

        if not (
            internal_formset.is_valid()
            and external_formset.is_valid()
        ):
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    formsets={
                        "internal": internal_formset,
                        "external": external_formset,
                    },
                )
            )
            
        with transaction.atomic():
            self.object = form.save()

            internal_formset.instance = self.object
            external_formset.instance = self.object

            internal_formset.save()
            external_formset.save()

        if self.success_message:
            messages.success(
                self.request,
                self.success_message,
            )

        return redirect(
            self.get_success_url()
        )

class MeetingCreateView(
    MeetingCompositeFormMixin,
    EPCreateView,
):
    """
    Création d'une réunion et de ses participants.
    """

    model = Meeting
    form_class = MeetingForm
    definition = MEETING_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = "La réunion a été créée avec succès."

    def get_initial(self):
        initial = super().get_initial()

        project_pk = self.request.GET.get("project")

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


class MeetingUpdateView(
    MeetingCompositeFormMixin,
    EPUpdateView,
):
    """
    Modification d'une réunion et de ses participants.
    """

    model = Meeting
    form_class = MeetingForm
    definition = MEETING_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = (
        "La réunion a été modifiée avec succès."
    )