

from __future__ import annotations
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.http import (
    url_has_allowed_host_and_scheme,
)
from django.db.models import (
    Case,
    CharField,
    F,
    Value,
    When,
)

from apps.core.models import ClientEnvironmentMembership
from django.views import View
from django.views.generic import FormView, ListView
from urllib.parse import quote

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)
from framework.integrations.django.list_preferences import (
    EPListPreferencesMixin,
)
from framework.integrations.django.list_sorting import (
    EPListSortingMixin,
)
from framework.runtime import EPList, ListPage
from framework.viewmodel.builder import ListViewModelBuilder
from .client_environment_membership_form import (
    ClientEnvironmentMembershipFormSet,
)
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
from .lists import CONTACT_LIST_DEFINITION
from .models import User
from .services import TemporaryPasswordService
from .services.access import UserAccessService
from apps.companies.models import Company


class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.must_change_password:
            return reverse_lazy(
                "users:password-change-required"
            )

        return super().get_success_url()


class UserAccessListQuerysetMixin:
    """
    Fournit le périmètre des utilisateurs visibles par l'acteur.
    """

    def get_queryset(self):
        return UserAccessService.get_accessible_users(
            self.request.user
        )


class UserListView(
    EPListSortingMixin,
    EPListPreferencesMixin,
    EPListPaginationMixin,
    ListView,
):
    model = ClientEnvironmentMembership
    template_name = "users/user_list.html"
    context_object_name = "contacts"

    list_definition = CONTACT_LIST_DEFINITION

    company_parameter = "company"
    activity_parameter = "activity"

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
                "last_name": "user__last_name",
                "first_name": "user__first_name",
                "email": "user__email",
                "phone": "user__phone",
                "client": (
                    "client_environment__company__name"
                ),
                "employment_type": "employment_type__label",
                "client_administration": (
                    "is_client_admin_responsible"
                ),
                "user_is_active": "user__is_active",
            }
        )

        return sort_field_map

    def get_filter_companies(self):
        memberships = (
            UserAccessService
            .get_accessible_client_environment_memberships(
                self.request.user
            )
        )

        environment_ids = (
            memberships
            .order_by()
            .values_list(
                "client_environment_id",
                flat=True,
            )
        )

        return (
            Company.objects
            .filter(
                client_environment__in=environment_ids,
            )
            .order_by("name")
        )

    def get_company_filter(self) -> str | None:
        raw_company_id = self.request.GET.get(
            self.company_parameter,
            "",
        ).strip()

        if not raw_company_id:
            return None

        try:
            company_id = UUID(raw_company_id)
        except ValueError:
            return None

        if not self.get_filter_companies().filter(
            pk=company_id,
        ).exists():
            return None

        return str(company_id)

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
            UserAccessService
            .get_accessible_client_environment_memberships(
                self.request.user
            )
            .annotate(
                last_name=F("user__last_name"),
                first_name=F("user__first_name"),
                email=F("user__email"),
                phone=F("user__phone"),
                client=F(
                    "client_environment__company__name"
                ),
                user_is_active=F("user__is_active"),
                client_administration=Case(
                    When(
                        is_client_admin_responsible=True,
                        then=Value(
                            "Administrateur client"
                        ),
                    ),
                    When(
                        is_client_admin=True,
                        then=Value(
                            "Administrateur client délégué"
                        ),
                    ),
                    default=Value(""),
                    output_field=CharField(),
                ),
            )
        )

        company_id = self.get_company_filter()

        if company_id is not None:
            queryset = queryset.filter(
                client_environment__company_id=company_id,
            )

        activity = self.get_activity_filter()

        if activity != self.activity_all:
            queryset = queryset.filter(
                user__is_active=(
                    activity == self.activity_active
                ),
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

        visible_column_identifiers = (
            self.get_visible_column_identifiers()
        )

        sort_by = self.get_sort_by()
        sort_descending = self.get_sort_descending()

        list_view = ListViewModelBuilder().build(
            runtime=runtime,
            page=framework_page,
            sort_by=sort_by,
            descending=sort_descending,
            visible_column_identifiers=(
                visible_column_identifiers
            ),
        )

        context["list_view"] = list_view
        context["list"] = list_view

        context["list_definition"] = (
            self.get_list_definition()
        )

        context["visible_column_identifiers"] = (
            visible_column_identifiers
        )

        context["can_save_list_preferences"] = (
            self.request.user.is_authenticated
        )

        context["sort_by"] = sort_by
        context["sort_descending"] = sort_descending

        context["filter_companies"] = (
            self.get_filter_companies()
        )

        context["company_filter"] = (
            self.get_company_filter()
        )

        context["user_activity"] = (
            self.get_activity_filter()
        )

        context["list_filters_template"] = (
            "users/user_list_filters.html"
        )

        context["row_actions_template"] = (
            "users/user_actions.html"
        )

        context["can_manage_client_environments"] = (
            UserAccessService.can_create_user(
                self.request.user
            )
        )

        context["user_create_url"] = (
            f"{reverse('users:create')}?next="
            f"{quote(self.request.get_full_path())}"
        )

        return context


class UserReturnUrlMixin:
    """
    Préserve l'état de la liste lors des actions sur un utilisateur.
    """

    def get_return_url(self):
        candidate = (
            self.request.POST.get(
                "next",
            )
            or self.request.GET.get(
                "next",
            )
        )

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    self.request.get_host(),
                },
                require_https=(
                    self.request.is_secure()
                ),
            )
        ):
            return candidate

        return reverse("users:list")

    def get_success_url(self):
        return self.get_return_url()

    def get_cancel_url(self):
        return self.get_return_url()
    
    
class UserFormCollectionsMixin:
    """
    Gère la collection des rattachements aux environnements
    clients associée au formulaire Utilisateur.
    """

    success_message = None

    def get_client_environment_membership_formset(
        self,
        *,
        data=None,
    ):
        return ClientEnvironmentMembershipFormSet(
            data=data,
            instance=self.object,
            prefix="client_environments",
            actor=self.request.user,
        )

    def get_formsets(
        self,
        *,
        django_form,
        context,
    ) -> dict:
        formset = context.get(
            "client_environment_membership_formset"
        )

        if formset is None:
            formset = (
                self.get_client_environment_membership_formset(
                    data=(
                        self.request.POST
                        if self.request.method == "POST"
                        else None
                    ),
                )
            )

            context[
                "client_environment_membership_formset"
            ] = formset

        return {
            "client_environments": formset,
        }

    def after_user_and_formsets_saved(self) -> None:
        """
        Point d'extension exécuté dans la transaction après
        l'enregistrement de l'utilisateur et des rattachements.
        """

    def form_valid(
        self,
        form,
    ):
        formset = (
            self.get_client_environment_membership_formset(
                data=self.request.POST,
            )
        )

        if not formset.is_valid():
            return self.render_to_response(
                self.get_context_data(
                    form=form,
                    client_environment_membership_formset=(
                        formset
                    ),
                )
            )

        with transaction.atomic():
            self.object = form.save()

            formset.instance = self.object
            formset.save()

            self.after_user_and_formsets_saved()

        if self.success_message:
            messages.success(
                self.request,
                self.success_message,
            )

        return redirect(
            self.get_success_url()
        )
        

class UserCreateView(
    UserReturnUrlMixin,
    UserFormCollectionsMixin,
    EPCreateView,
):
    model = User
    form_class = UserForm
    definition = USER_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = (
        "L'utilisateur a été créé avec succès. "
        "Son mot de passe provisoire lui a été "
        "envoyé par e-mail."
    )

    def dispatch(
        self,
        request,
        *args,
        **kwargs,
    ):
        if not UserAccessService.can_create_user(
            request.user
        ):
            raise PermissionDenied

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def after_user_and_formsets_saved(self) -> None:
        """
        L'envoi intervient dans la transaction. Une erreur
        d'envoi annule donc aussi la création de l'utilisateur
        et de ses rattachements.
        """
        TemporaryPasswordService.reset_and_send(
            user=self.object,
        )


class UserUpdateView(
    UserReturnUrlMixin,
    UserFormCollectionsMixin,
    EPUpdateView,
):
    model = User
    form_class = UserForm
    definition = USER_FORM_DEFINITION
    template_name = "edf/form/view.html"

    success_message = (
        "L'utilisateur a été modifié avec succès."
    )

    def get_queryset(self):
        return UserAccessService.get_accessible_users(
            self.request.user
        )

    def get_object(self, queryset=None):
        user = super().get_object(queryset)

        if not UserAccessService.can_update_user(
            self.request.user,
            user,
        ):
            raise Http404

        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs
    

class UserTemporaryPasswordResendView(
    UserReturnUrlMixin,
    View,
):
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
            UserAccessService.get_accessible_users(
                request.user
            ),
            pk=pk,
        )

        if not (
            UserAccessService
            .can_reset_temporary_password(
                request.user,
                user,
            )
        ):
            raise Http404

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
            self.get_return_url()
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