

from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView

from apps.core.models import ClientEnvironmentMembership
from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import (
    ListViewModelBuilder,
)

from .client_environment_membership_form import (
    ClientEnvironmentMembershipForm,
)
from .client_environment_membership_form_definition import (
    CLIENT_ENVIRONMENT_MEMBERSHIP_FORM_DEFINITION,
)
from .lists import (
    CLIENT_ENVIRONMENT_MEMBERSHIP_LIST_DEFINITION,
)
from .models import User
from .services.access import UserAccessService


class ClientEnvironmentMembershipListView(
    EPListPaginationMixin,
    ListView,
):
    model = ClientEnvironmentMembership
    template_name = (
        "users/client_environment_membership_list.html"
    )
    context_object_name = (
        "client_environment_memberships"
    )

    def get_target_user(self) -> User:
        if not hasattr(self, "_target_user"):
            self._target_user = get_object_or_404(
                UserAccessService.get_accessible_users(
                    self.request.user
                ),
                pk=self.kwargs["user_pk"],
            )

        return self._target_user

    def get_queryset(self):
        return (
            UserAccessService
            .get_administrable_client_environment_memberships(
                self.request.user,
                self.get_target_user(),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]
        target_user = self.get_target_user()

        runtime = EPList(
            definition=(
                CLIENT_ENVIRONMENT_MEMBERSHIP_LIST_DEFINITION
            ),
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
        context["target_user"] = target_user
        context["row_actions_template"] = (
            "users/client_environment_membership_actions.html"
        )

        context["page_title"] = (
            "Accès aux environnements clients"
        )
        context["page_subtitle"] = (
            f"{target_user.last_name} "
            f"{target_user.first_name}"
        )
        context["page_back_url"] = reverse(
            "users:list"
        )
        context["page_back_label"] = (
            "Retour aux utilisateurs"
        )

        if (
            UserAccessService
            .can_create_client_environment_membership(
                self.request.user,
                target_user,
            )
        ):
            context["page_action_label"] = (
                "Nouveau rattachement"
            )
            context["page_action_icon"] = "plus"
            context["page_action_url"] = reverse(
                (
                    "users:"
                    "client-environment-membership-create"
                ),
                kwargs={
                    "user_pk": target_user.pk,
                },
            )
        else:
            context["page_action_label"] = None
            context["page_action_icon"] = None
            context["page_action_url"] = None

        return context


class ClientEnvironmentMembershipCreateView(
    EPCreateView,
):
    model = ClientEnvironmentMembership
    form_class = ClientEnvironmentMembershipForm
    definition = (
        CLIENT_ENVIRONMENT_MEMBERSHIP_FORM_DEFINITION
    )
    template_name = "edf/form/view.html"

    def get_target_user(self) -> User:
        if not hasattr(self, "_target_user"):
            self._target_user = get_object_or_404(
                UserAccessService.get_accessible_users(
                    self.request.user
                ),
                pk=self.kwargs["user_pk"],
            )

        return self._target_user

    def dispatch(self, request, *args, **kwargs):
        target_user = self.get_target_user()

        if not (
            UserAccessService
            .can_create_client_environment_membership(
                request.user,
                target_user,
            )
        ):
            raise PermissionDenied

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["actor"] = self.request.user
        kwargs["target_user"] = self.get_target_user()

        return kwargs

    def get_return_url(self):
        return reverse(
            "users:client-environment-membership-list",
            kwargs={
                "user_pk": self.get_target_user().pk,
            },
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le rattachement client a été créé.",
        )

        return response


class ClientEnvironmentMembershipUpdateView(
    EPUpdateView,
):
    model = ClientEnvironmentMembership
    form_class = ClientEnvironmentMembershipForm
    definition = (
        CLIENT_ENVIRONMENT_MEMBERSHIP_FORM_DEFINITION
    )
    template_name = "edf/form/view.html"

    def get_target_user(self) -> User:
        if not hasattr(self, "_target_user"):
            self._target_user = get_object_or_404(
                UserAccessService.get_accessible_users(
                    self.request.user
                ),
                pk=self.kwargs["user_pk"],
            )

        return self._target_user

    def get_queryset(self):
        return (
            UserAccessService
            .get_administrable_client_environment_memberships(
                self.request.user,
                self.get_target_user(),
            )
        )

    def get_object(self, queryset=None):
        membership = super().get_object(queryset)

        if not (
            UserAccessService
            .can_update_client_environment_membership(
                self.request.user,
                membership,
            )
        ):
            raise Http404

        return membership

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["actor"] = self.request.user
        kwargs["target_user"] = self.get_target_user()

        return kwargs

    def get_return_url(self):
        return reverse(
            "users:client-environment-membership-list",
            kwargs={
                "user_pk": self.get_target_user().pk,
            },
        )

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "Le rattachement client a été modifié.",
        )

        return response