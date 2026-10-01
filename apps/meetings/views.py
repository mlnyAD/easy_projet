from urllib.parse import urlencode
from uuid import UUID


from django.contrib import messages

from django.contrib.auth.mixins import UserPassesTestMixin

from django.db import transaction

from django.shortcuts import get_object_or_404, redirect

from django.urls import reverse

from django.utils.http import url_has_allowed_host_and_scheme

from django.http import JsonResponse

from django.core.exceptions import PermissionDenied

from django.views import View

from django.views.generic import ListView


from apps.projects.models import Project, ProjectMembership

from apps.projects.services.access import (
    ProjectAccessService,
)

from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)
from apps.catalogs.models import CatalogValue
from apps.users.models import User

from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)
from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)

from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)

from framework.runtime import EPList, ListPage

from framework.integrations.django.viewmodel import (
    DjangoListViewModelBuilder,
)

from apps.users.models import User


from .form_definition import MEETING_FORM_DEFINITION

from .forms import (
    ExternalMeetingParticipantFormSet,
    InternalMeetingParticipantFormSet,
    MeetingForm,
)

from .lists import MEETING_LIST_DEFINITION

from .models import Meeting

from .services.invitations import (
    MeetingInvitationError,
    MeetingInvitationService,
)


def get_allowed_return_url(
    request,
    *,
    default_url,
):

    candidate = request.GET.get("next")

    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate

    return default_url


class MeetingListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    """
    Liste globale des réunions accessibles.
    """

    model = Meeting
    template_name = "meetings/meeting_list.html"
    context_object_name = "meetings"

    list_definition = MEETING_LIST_DEFINITION

    project_parameter = "project"
    organizer_parameter = "organizer"
    status_parameter = "status"
    invitations_parameter = "invitations"
    activity_parameter = "activity"

    invitations_all = "all"
    invitations_sent = "sent"
    invitations_pending = "pending"

    invitations_values = (
        invitations_all,
        invitations_sent,
        invitations_pending,
    )

    activity_all = "all"
    activity_active = "active"
    activity_inactive = "inactive"

    activity_values = (
        activity_all,
        activity_active,
        activity_inactive,
    )

    def get_sort_field_map(self) -> dict[str, str]:
        sort_field_map = super().get_sort_field_map()

        sort_field_map.update(
            {
                "project": "project__reference",
                "organizer": "organizer__last_name",
                "status": "status__sort_order",
                "invitations_sent": "invitations_sent_at",
            }
        )

        return sort_field_map

    def get_accessible_projects(self):
        return ProjectAccessService.get_accessible_projects(self.request.user)

    def get_meeting_scope(self):
        return Meeting.objects.filter(
            project__in=self.get_accessible_projects(),
        ).select_related(
            "project",
            "organizer",
            "status",
        )

    def get_filter_projects(self):
        return self.get_accessible_projects().order_by(
            "reference",
            "name",
        )

    def get_filter_organizers(self):
        organizer_ids = self.get_meeting_scope().values_list(
            "organizer_id",
            flat=True,
        )

        return User.objects.filter(
            pk__in=organizer_ids,
        ).order_by(
            "last_name",
            "first_name",
        )

    def get_filter_statuses(self):
        status_ids = self.get_meeting_scope().values_list(
            "status_id",
            flat=True,
        )

        return CatalogValue.objects.filter(
            pk__in=status_ids,
        ).order_by(
            "sort_order",
            "label",
        )

    def get_project_filter(self) -> str | None:
        raw_project_id = self.request.GET.get(
            self.project_parameter,
            "",
        ).strip()

        if not raw_project_id:
            return None

        try:
            project_id = UUID(raw_project_id)
        except ValueError:
            return None

        if (
            not self.get_filter_projects()
            .filter(
                pk=project_id,
            )
            .exists()
        ):
            return None

        return str(project_id)

    def get_organizer_filter(self) -> str | None:
        raw_organizer_id = self.request.GET.get(
            self.organizer_parameter,
            "",
        ).strip()

        if not raw_organizer_id:
            return None

        try:
            organizer_id = UUID(raw_organizer_id)
        except ValueError:
            return None

        if (
            not self.get_filter_organizers()
            .filter(
                pk=organizer_id,
            )
            .exists()
        ):
            return None

        return str(organizer_id)

    def get_status_filter(self) -> int | None:
        raw_status_id = self.request.GET.get(
            self.status_parameter,
            "",
        ).strip()

        if not raw_status_id:
            return None

        try:
            status_id = int(raw_status_id)
        except ValueError:
            return None

        if (
            not self.get_filter_statuses()
            .filter(
                pk=status_id,
            )
            .exists()
        ):
            return None

        return status_id

    def get_invitations_filter(self) -> str:
        invitations = self.request.GET.get(
            self.invitations_parameter,
            self.invitations_all,
        )

        if invitations not in self.invitations_values:
            return self.invitations_all

        return invitations

    def get_activity_filter(self) -> str:
        activity = self.request.GET.get(
            self.activity_parameter,
            self.activity_active,
        )

        if activity not in self.activity_values:
            return self.activity_active

        return activity

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(pk__in=self.get_meeting_scope())
            .select_related(
                "project",
                "organizer",
                "status",
            )
        )

        project_id = self.get_project_filter()
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)

        organizer_id = self.get_organizer_filter()
        if organizer_id is not None:
            queryset = queryset.filter(organizer_id=organizer_id)

        status_id = self.get_status_filter()
        if status_id is not None:
            queryset = queryset.filter(status_id=status_id)

        invitations = self.get_invitations_filter()
        if invitations == self.invitations_sent:
            queryset = queryset.filter(
                invitations_sent_at__isnull=False,
            )
        elif invitations == self.invitations_pending:
            queryset = queryset.filter(
                invitations_sent_at__isnull=True,
            )

        activity = self.get_activity_filter()
        if activity != self.activity_all:
            queryset = queryset.filter(
                is_active=activity == self.activity_active,
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=self.list_definition,
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

        visible_column_identifiers = self.get_visible_column_identifiers()
        sort_by = self.get_sort_by()
        sort_descending = self.get_sort_descending()

        list_view = DjangoListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
            sort_by=sort_by,
            descending=sort_descending,
            visible_column_identifiers=(visible_column_identifiers),
        )

        context["list_view"] = list_view
        context["list"] = list_view

        context["list_definition"] = self.get_list_definition()
        context["visible_column_identifiers"] = visible_column_identifiers
        context["can_save_list_preferences"] = self.request.user.is_authenticated

        context["sort_by"] = sort_by
        context["sort_descending"] = sort_descending

        context["filter_projects"] = self.get_filter_projects()
        context["filter_organizers"] = self.get_filter_organizers()
        context["filter_statuses"] = self.get_filter_statuses()

        context["project_filter"] = self.get_project_filter()
        context["organizer_filter"] = self.get_organizer_filter()
        context["status_filter"] = self.get_status_filter()
        context["meeting_invitations"] = self.get_invitations_filter()
        context["meeting_activity"] = self.get_activity_filter()

        context["list_filters_template"] = "meetings/meeting_list_filters.html"
        context["row_actions_template"] = "meetings/meeting_actions.html"

        context["is_project_context"] = False
        context["return_url"] = self.request.get_full_path()
        context["current_list_url"] = self.request.get_full_path()

        context["page_title"] = "Réunions"
        context["page_subtitle"] = None
        context["page_back_url"] = None
        context["page_back_label"] = None

        can_create = ProjectAuthorizationService.get_workable_projects(
            self.request.user
        ).exists()

        context["page_action_label"] = "Nouvelle réunion" if can_create else None
        context["page_action_icon"] = "plus" if can_create else None
        context["page_action_url"] = (
            (
                f"{reverse('meetings:create')}?"
                f"{urlencode({'next': self.request.get_full_path()})}"
            )
            if can_create
            else None
        )

        return context


class MeetingListByProjectView(MeetingListView):
    """

    Liste des réunions d'un projet accessible.

    """

    def get_project(self) -> Project:

        if not hasattr(self, "_project"):
            self._project = get_object_or_404(
                ProjectAccessService.get_accessible_projects(
                    self.request.user
                ).select_related(
                    "owner_company",
                    "status",
                ),
                pk=self.kwargs["project_pk"],
            )

        return self._project

    def get_meeting_scope(self):
        return (
            super()
            .get_meeting_scope()
            .filter(
                project=self.get_project(),
            )
        )

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        project = self.get_project()

        context["project"] = project

        context["current_project"] = project

        context["is_project_context"] = True

        context["return_url"] = self.request.get_full_path()

        context["current_list_url"] = self.request.get_full_path()

        context["page_title"] = "Réunions du projet"

        context["page_subtitle"] = f"{project.reference} — {project.name}"

        context["page_back_url"] = reverse(
            "projects:workspace",
            kwargs={
                "pk": project.pk,
            },
        )

        context["page_back_label"] = "Retour au projet"

        if ProjectAuthorizationService.can_work_on_project(
            user=self.request.user,
            project=project,
        ):
            context["page_action_label"] = "Nouvelle réunion"

            context["page_action_icon"] = "plus"

            context["page_action_url"] = (
                f"{reverse('meetings:create')}?"
                f"{
                    urlencode(
                        {
                            'next': self.request.get_full_path(),
                            'project': project.pk,
                        }
                    )
                }"
            )

        else:
            context["page_action_label"] = None

            context["page_action_icon"] = None

            context["page_action_url"] = None

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
        project=None,
    ):

        if instance is None:
            instance = self.object

        return InternalMeetingParticipantFormSet(
            data=data,
            instance=instance,
            prefix="internal",
            project=project,
            form_kwargs={"project": project},
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

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def get_formsets(
        self,
        *,
        django_form,
        context,
    ):

        if "formsets" in context:
            return context["formsets"]

        instance = django_form.instance

        project = self._get_form_project(
            django_form=django_form,
        )

        data = self.request.POST if self.request.method == "POST" else None

        return {
            "internal": self.get_internal_formset(
                data=data,
                instance=instance,
                project=project,
            ),
            "external": self.get_external_formset(
                data=data,
                instance=instance,
            ),
        }

    @staticmethod
    def _get_form_project(*, django_form):

        if django_form.is_bound:
            project_id = django_form.data.get(django_form.add_prefix("project"))

            return (
                django_form.fields["project"]
                .queryset.filter(
                    pk=project_id,
                )
                .first()
            )

        if django_form.instance.project_id:
            return django_form.instance.project

        project_id = django_form.initial.get("project")

        return (
            django_form.fields["project"]
            .queryset.filter(
                pk=project_id,
            )
            .first()
        )

    def form_valid(self, form):

        instance = form.instance

        project = form.cleaned_data["project"]

        meeting_changed = form.has_changed()

        internal_formset = self.get_internal_formset(
            data=self.request.POST,
            instance=instance,
            project=project,
        )

        external_formset = self.get_external_formset(
            data=self.request.POST,
            instance=instance,
        )

        if not (internal_formset.is_valid() and external_formset.is_valid()):
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

            if self.object.invitations_sent_at is not None and (
                meeting_changed
                or internal_formset.has_changed()
                or external_formset.has_changed()
            ):
                self.object.invitations_sent_at = None

                self.object.save(
                    update_fields=[
                        "invitations_sent_at",
                        "updated_at",
                    ]
                )

                messages.info(
                    self.request,
                    "Les invitations devront être envoyées à nouveau.",
                )

        if self.success_message:
            messages.success(
                self.request,
                self.success_message,
            )

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        meeting = getattr(self, "object", None)

        if meeting is None or meeting.pk is None:
            context["can_send_invitations"] = False

            context["meeting_invitation_url"] = None

            return context

        can_send = ProjectAuthorizationService.can_work_on_project(
            user=self.request.user,
            project=meeting.project,
        )

        context["can_send_invitations"] = can_send

        context["meeting_invitation_url"] = reverse(
            "meetings:send-invitations",
            kwargs={"pk": meeting.pk},
        )

        return context


class MeetingCreateView(
    UserPassesTestMixin,
    MeetingCompositeFormMixin,
    EPCreateView,
):
    """

    Création d'une réunion et de ses participants.

    """

    model = Meeting

    form_class = MeetingForm

    definition = MEETING_FORM_DEFINITION

    template_name = "meetings/meeting_form.html"

    success_message = "La réunion a été créée avec succès."

    def test_func(self):

        return ProjectAuthorizationService.get_workable_projects(
            self.request.user
        ).exists()

    def get_initial(self):

        initial = super().get_initial()

        project_pk = self.request.GET.get("project")

        if project_pk:
            project = (
                ProjectAuthorizationService.get_workable_projects(self.request.user)
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

    template_name = "meetings/meeting_form.html"

    success_message = "La réunion a été modifiée avec succès."

    def get_queryset(self):

        accessible_projects = ProjectAccessService.get_accessible_projects(
            self.request.user
        )

        return Meeting.objects.filter(
            project__in=accessible_projects,
        ).select_related(
            "project",
            "organizer",
            "status",
        )

    def can_edit_object(self) -> bool:
        """

        Indique si l'utilisateur peut modifier la réunion courante.



        Une réunion visible sur un projet non modifiable est ouverte

        en lecture seule.

        """

        return ProjectAuthorizationService.can_work_on_project(
            user=self.request.user,
            project=self.object.project,
        )


class MeetingProjectUsersView(View):
    """Retourne les choix dépendant du projet du formulaire."""

    def get(self, request):

        project = get_object_or_404(
            ProjectAuthorizationService.get_workable_projects(request.user),
            pk=request.GET.get("project"),
            is_active=True,
        )

        organizers = User.objects.filter(
            company_id=project.company_id,
            is_active=True,
        ).order_by("last_name", "first_name")

        participant_ids = ProjectMembership.objects.filter(
            project=project,
            is_active=True,
            user__is_active=True,
        ).values_list("user_id", flat=True)

        participants = User.objects.filter(
            pk__in=participant_ids,
            is_active=True,
        ).order_by("last_name", "first_name")

        return JsonResponse(
            {
                "organizers": [
                    {"id": str(user.pk), "label": str(user)} for user in organizers
                ],
                "participants": [
                    {"id": str(user.pk), "label": str(user)} for user in participants
                ],
            }
        )


class MeetingSendInvitationsView(View):
    """Déclenche volontairement l'envoi des invitations."""

    def post(self, request, *, pk):

        meeting = get_object_or_404(
            Meeting.objects.select_related("project"),
            pk=pk,
            project__in=ProjectAccessService.get_accessible_projects(request.user),
        )

        if not ProjectAuthorizationService.can_work_on_project(
            user=request.user,
            project=meeting.project,
        ):
            raise PermissionDenied

        try:
            result = MeetingInvitationService.send(
                meeting=meeting,
                author=request.user,
            )

        except MeetingInvitationError as error:
            messages.error(request, str(error))

        else:
            if result.email_failed:
                messages.warning(
                    request,
                    "La notification interne a été créée, mais "
                    "l'envoi des emails externes a échoué.",
                )

            else:
                messages.success(
                    request,
                    "Les invitations ont été envoyées.",
                )

        return redirect(
            get_allowed_return_url(
                request,
                default_url=reverse(
                    "meetings:update",
                    kwargs={"pk": meeting.pk},
                ),
            )
        )
