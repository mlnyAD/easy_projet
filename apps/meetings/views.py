

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

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

from .form_definition import (
    MEETING_FORM_DEFINITION,
    MEETING_PARTICIPANT_FORM_DEFINITION,
)
from .forms import (
    MeetingForm,
    MeetingParticipantForm,
)
from .lists import (
    MEETING_LIST_DEFINITION,
    MEETING_PARTICIPANT_LIST_DEFINITION,
)
from .models import (
    Meeting,
    MeetingParticipant,
)


def get_allowed_return_url(
    request,
    *,
    default_url,
):
    """
    Retourne une URL locale sécurisée issue du paramètre next.
    """
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

        # Retour après création ou modification d'une réunion.
        context["return_url"] = self.request.get_full_path()

        # Accès à un écran enfant, tel que les participants.
        context["current_list_url"] = (
            self.request.get_full_path()
        )

        return context


class MeetingListByProjectView(MeetingListView):
    """
    Liste des réunions d'un projet donné.
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

        # Après création ou modification : résumé du projet.
        context["return_url"] = reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )

        # Après consultation des participants : liste des réunions.
        context["current_list_url"] = (
            self.request.get_full_path()
        )

        return context


class MeetingCreateView(EPCreateView):
    model = Meeting
    form_class = MeetingForm
    definition = MEETING_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse_lazy("meetings:list"),
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

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

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La réunion a été créée avec succès.",
        )

        return response


class MeetingUpdateView(EPUpdateView):
    model = Meeting
    form_class = MeetingForm
    definition = MEETING_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse_lazy("meetings:list"),
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "La réunion a été modifiée avec succès.",
        )

        return response


class MeetingParticipantListView(ListView):
    """
    Liste des participants d'une réunion.
    """

    model = MeetingParticipant
    template_name = "meetings/participant_list.html"
    context_object_name = "participants"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_meeting(self) -> Meeting:
        if not hasattr(self, "_meeting"):
            self._meeting = get_object_or_404(
                Meeting.objects.select_related(
                    "project",
                    "organizer",
                    "status",
                ),
                pk=self.kwargs["meeting_pk"],
            )

        return self._meeting

    def get_queryset(self):
        return (
            MeetingParticipant.objects
            .filter(
                meeting=self.get_meeting(),
            )
            .select_related(
                "meeting",
                "participant",
                "invitation_response",
            )
            .order_by(
                "participant__last_name",
                "participant__first_name",
                "external_name",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        meeting = self.get_meeting()
        django_page = context["page_obj"]

        runtime = EPList(
            definition=MEETING_PARTICIPANT_LIST_DEFINITION,
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
            "meetings/participant_actions.html"
        )

        context["meeting"] = meeting
        context["current_project"] = meeting.project

        # Création/modification : retour aux participants.
        context["return_url"] = self.request.get_full_path()

        # Sortie de l'écran participants : retour à l'écran appelant.
        context["parent_return_url"] = (
            get_allowed_return_url(
                self.request,
                default_url=reverse(
                    "meetings:list-by-project",
                    kwargs={
                        "project_pk": meeting.project_id,
                    },
                ),
            )
        )

        return context


class MeetingParticipantCreateView(EPCreateView):
    model = MeetingParticipant
    form_class = MeetingParticipantForm
    definition = MEETING_PARTICIPANT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_meeting(self) -> Meeting:
        if not hasattr(self, "_meeting"):
            self._meeting = get_object_or_404(
                Meeting.objects.select_related(
                    "project",
                ),
                pk=self.kwargs["meeting_pk"],
            )

        return self._meeting

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse(
                "meetings:participant-list",
                kwargs={
                    "meeting_pk": self.get_meeting().pk,
                },
            ),
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_initial(self):
        initial = super().get_initial()
        initial["meeting"] = self.get_meeting()
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["meeting"].initial = self.get_meeting()
        form.fields["meeting"].disabled = True

        return form

    def form_valid(self, form):
        form.instance.meeting = self.get_meeting()

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le participant a été ajouté avec succès.",
        )

        return response


class MeetingParticipantUpdateView(EPUpdateView):
    model = MeetingParticipant
    form_class = MeetingParticipantForm
    definition = MEETING_PARTICIPANT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_meeting(self) -> Meeting:
        if not hasattr(self, "_meeting"):
            self._meeting = get_object_or_404(
                Meeting.objects.select_related(
                    "project",
                ),
                pk=self.kwargs["meeting_pk"],
            )

        return self._meeting

    def get_queryset(self):
        return (
            MeetingParticipant.objects
            .filter(
                meeting=self.get_meeting(),
            )
            .select_related(
                "meeting",
                "participant",
                "invitation_response",
            )
        )

    def get_return_url(self):
        return get_allowed_return_url(
            self.request,
            default_url=reverse(
                "meetings:participant-list",
                kwargs={
                    "meeting_pk": self.get_meeting().pk,
                },
            ),
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["meeting"].disabled = True

        return form

    def form_valid(self, form):
        form.instance.meeting = self.get_meeting()

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le participant a été modifié avec succès.",
        )

        return response