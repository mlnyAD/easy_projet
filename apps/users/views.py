

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import FormView

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder

from .account_form_definition import (
    ACCOUNT_FORM_DEFINITION,
)
from .form_definition import USER_FORM_DEFINITION
from .forms import (
    AccountForm,
    RequiredPasswordChangeForm,
    UserForm,
    UserLoginForm,
)
from .lists import USER_LIST_DEFINITION
from .models import User
from .services import TemporaryPasswordService


class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if (
            self.request.user
            .must_change_password
        ):
            return reverse_lazy(
                "users:password-change-required"
            )

        return super().get_success_url()

class UserListView(
    EPListPaginationMixin,
    ListView,
):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return (
            User.objects
            .select_related(
                "company",
                "global_role",
                "access_level",
                "employment_type",
                "job",
            )
            .order_by(
                "last_name",
                "first_name",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        django_page = context["page_obj"]

        runtime = EPList(
            definition=USER_LIST_DEFINITION,
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
        context["list"] = list_view
        context["row_actions_template"] = (
            "users/user_actions.html"
        )

        return context


class UserCreateView(EPCreateView):
    model = User
    form_class = UserForm
    definition = USER_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("users:list")
    cancel_url = reverse_lazy("users:list")

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)

        TemporaryPasswordService.reset_and_send(
            user=self.object,
        )

        messages.success(
            self.request,
            (
                "L'utilisateur a été créé avec succès. "
                "Son mot de passe provisoire lui a été "
                "envoyé par e-mail."
            ),
        )

        return response


class UserUpdateView(EPUpdateView):
    model = User
    form_class = UserForm
    definition = USER_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("users:list")
    cancel_url = reverse_lazy("users:list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "L'utilisateur a été modifié avec succès.",
        )

        return response


class UserTemporaryPasswordResendView(View):
    """
    Régénère et renvoie un mot de passe provisoire.

    Cette action invalide immédiatement le mot de passe
    précédemment associé au compte.
    """

    http_method_names = [
        "post",
    ]

    def post(
        self,
        request,
        pk,
    ):
        user = get_object_or_404(
            User,
            pk=pk,
        )

        TemporaryPasswordService.reset_and_send(
            user=user,
        )

        messages.success(
            request,
            (
                "Un nouveau mot de passe provisoire "
                f"a été envoyé à {user.email}."
            ),
        )

        return redirect(
            "users:list"
        )


class AccountUpdateView(EPUpdateView):
    model = User
    form_class = AccountForm
    definition = ACCOUNT_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_url = reverse_lazy("home")
    cancel_url = reverse_lazy("home")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        password_changed = bool(
            form.cleaned_data.get("new_password")
        )

        response = super().form_valid(form)

        if password_changed:
            update_session_auth_hash(
                self.request,
                form.instance,
            )

        messages.success(
            self.request,
            "Votre compte a été mis à jour.",
        )

        return response
    
class RequiredPasswordChangeView(
    LoginRequiredMixin,
    FormView,
):
    """
    Oblige l'utilisateur connecté avec un mot
    de passe provisoire à définir son mot
    de passe personnel.
    """

    template_name = (
        "users/password_change_required.html"
    )

    form_class = (
        RequiredPasswordChangeForm
    )

    success_url = reverse_lazy(
        "home"
    )

    def dispatch(
        self,
        request,
        *args,
        **kwargs,
    ):
        if (
            request.user.is_authenticated
            and not request.user.must_change_password
        ):
            return redirect(
                "home"
            )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_form_kwargs(self):
        kwargs = (
            super().get_form_kwargs()
        )

        kwargs["user"] = (
            self.request.user
        )

        return kwargs

    def form_valid(
        self,
        form,
    ):
        user = form.save()

        update_session_auth_hash(
            self.request,
            user,
        )

        messages.success(
            self.request,
            "Votre mot de passe personnel a été enregistré.",
        )

        return super().form_valid(
            form
        )