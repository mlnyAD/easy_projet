

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView

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

from .form_definition import USER_FORM_DEFINITION
from .forms import UserForm
from .lists import USER_LIST_DEFINITION
from .models import User
from django.contrib.auth import update_session_auth_hash

from .account_form_definition import (
    ACCOUNT_FORM_DEFINITION,
)
from .forms import AccountForm


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = DEFAULT_PAGE_SIZE

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

        # Alias temporaire pour compatibilité.
        context["list"] = list_view

        context["page_sizes"] = PAGE_SIZE_VALUES
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

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            "L'utilisateur a été créé avec succès.",
        )

        # L'envoi de l'invitation sera ajouté ici lorsque
        # le service d'invitation sera disponible.

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