

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import url_has_allowed_host_and_scheme

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
from framework.integrations.django.views import EPCreateView
from framework.runtime import (
    EPList,
    ListPage,
)
from framework.viewmodel.builder import (
    ListViewModelBuilder,
)
from .forms import (
    TodoActionForm,
    TodoActionRecipientFormSet,
)
from .form_definition import TODO_ACTION_FORM_DEFINITION
from .lists import TODO_LIST_DEFINITION
from .models import TodoAction
from .selectors import get_user_todo_actions

from framework.integrations.django.views import (
    EPCreateView,
    EPUpdateView,
)


class TodoListView(
    LoginRequiredMixin,
    EPListPaginationMixin,
    ListView,
):
    """
    Todo courant de l'utilisateur connecté.

    La vue affiche uniquement les actions
    nécessitant encore son attention.
    """

    model = TodoAction

    template_name = (
        "todos/todo_list.html"
    )

    context_object_name = "todo_actions"

    def get_queryset(self):
        return (
            get_user_todo_actions(
                user=self.request.user,
            )
            .filter(
                status__in=(
                    TodoAction.Status.TODO,
                    TodoAction.Status.IN_PROGRESS,
                    TodoAction.Status.SUSPENDED,
                )
            )
            .order_by(
                F("due_date").asc(
                    nulls_last=True
                ),
                "created_at",
            )
        )

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs
        )

        django_page = context[
            "page_obj"
        ]

        for action in django_page.object_list:
            action.can_manage = (
                action.owner_id
                == self.request.user.pk
            )
            
        runtime = EPList(
            definition=TODO_LIST_DEFINITION,
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

        # Alias temporaire identique
        # aux autres listes Easy Projet.
        context["list"] = list_view

        context["row_actions_template"] = (
            "todos/todo_actions.html"
        )

        return context


class TodoActionCreateView(
    LoginRequiredMixin,
    EPCreateView,
):
    """
    Création d'une action Todo et de ses destinataires.
    """

    model = TodoAction
    form_class = TodoActionForm
    definition = TODO_ACTION_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_cancel_url(self) -> str:
        return reverse("todos:list")

    def get_success_url(self) -> str:
        return reverse("todos:list")

    def get_formsets(
        self,
        *,
        django_form,
        context,
    ) -> dict:
        return {
            "recipients": self.get_recipient_formset(
                form=django_form,
            ),
        }

    def get_recipient_formset(
        self,
        *,
        form,
    ):
        if not hasattr(
            self,
            "_recipient_formset",
        ):
            self._recipient_formset = (
                TodoActionRecipientFormSet(
                    data=(
                        self.request.POST
                        if self.request.method == "POST"
                        else None
                    ),
                    instance=form.instance,
                    prefix="recipients",
                )
            )

        return self._recipient_formset

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs,
        )

        context["form_extra_template"] = (
            "todos/todo_action_form_extra.html"
        )

        return context

    def form_valid(self, form):
        recipient_formset = (
            self.get_recipient_formset(
                form=form,
            )
        )

        formset_valid = recipient_formset.is_valid()

        business_rules_valid = (
            formset_valid
            and self._validate_business_rules(
                form=form,
                recipient_formset=recipient_formset,
            )
        )

        if not (
            formset_valid
            and business_rules_valid
        ):
            messages.error(
                self.request,
                "Certaines informations sont incorrectes.",
            )

            return self.render_to_response(
                self.get_context_data(
                    form=form,
                )
            )

        with transaction.atomic():
            action = form.save(
                commit=False,
            )

            action.owner = self.request.user
            action.status = TodoAction.Status.TODO

            action.full_clean()
            action.save()

            recipient_formset.instance = action
            recipient_formset.save()

        self.object = action

        messages.success(
            self.request,
            "L'action a été créée.",
        )

        return redirect(
            self.get_success_url()
        )

    def _validate_business_rules(
        self,
        *,
        form,
        recipient_formset,
    ) -> bool:
        origin = form.cleaned_data.get(
            "origin"
        )

        active_recipient_forms = []

        for recipient_form in recipient_formset.forms:
            cleaned_data = getattr(
                recipient_form,
                "cleaned_data",
                None,
            )

            if not cleaned_data:
                continue

            if cleaned_data.get("DELETE"):
                continue

            if cleaned_data.get("user"):
                active_recipient_forms.append(
                    recipient_form
                )

        if (
            origin == TodoAction.Origin.PERSONAL
            and active_recipient_forms
        ):
            form.add_error(
                "origin",
                (
                    "Une action personnelle ne peut pas "
                    "avoir de destinataire."
                ),
            )

            return False

        if (
            origin == TodoAction.Origin.ASSIGNED
            and not active_recipient_forms
        ):
            form.add_error(
                "origin",
                (
                    "Une action assignée doit avoir "
                    "au moins un destinataire."
                ),
            )

            return False

        return True
    

class TodoActionReturnUrlMixin:
    """
    Préserve le contexte d'origine de la liste Todo.
    """

    def get_return_url(self) -> str:
        candidate = (
            self.request.GET.get("next")
            or self.request.POST.get("next")
            or ""
        ).strip()

        if (
            candidate
            and url_has_allowed_host_and_scheme(
                candidate,
                allowed_hosts={
                    self.request.get_host(),
                },
                require_https=self.request.is_secure(),
            )
        ):
            return candidate

        return reverse("todos:list")

    def get_success_url(self) -> str:
        return self.get_return_url()

    def get_cancel_url(self) -> str:
        return self.get_return_url()


class TodoActionFormsetMixin:
    """
    Gestion commune du formset des destinataires.
    """

    def get_formsets(
        self,
        *,
        django_form,
        context,
    ) -> dict:
        return {
            "recipients": self.get_recipient_formset(
                form=django_form,
            ),
        }

    def get_recipient_formset(
        self,
        *,
        form,
    ):
        if not hasattr(
            self,
            "_recipient_formset",
        ):
            self._recipient_formset = (
                TodoActionRecipientFormSet(
                    data=(
                        self.request.POST
                        if self.request.method == "POST"
                        else None
                    ),
                    instance=form.instance,
                    prefix="recipients",
                )
            )

        return self._recipient_formset

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(
            **kwargs,
        )

        context["form_extra_template"] = (
            "todos/todo_action_form_extra.html"
        )

        return context

    def validate_business_rules(
        self,
        *,
        form,
        recipient_formset,
    ) -> bool:
        origin = form.cleaned_data.get("origin")

        active_recipient_forms = []

        for recipient_form in recipient_formset.forms:
            cleaned_data = getattr(
                recipient_form,
                "cleaned_data",
                None,
            )

            if (
                not cleaned_data
                or cleaned_data.get("DELETE")
            ):
                continue

            if cleaned_data.get("user"):
                active_recipient_forms.append(
                    recipient_form
                )

        if (
            origin == TodoAction.Origin.PERSONAL
            and active_recipient_forms
        ):
            form.add_error(
                "origin",
                (
                    "Une action personnelle ne peut pas "
                    "avoir de destinataire."
                ),
            )
            return False

        if (
            origin == TodoAction.Origin.ASSIGNED
            and not active_recipient_forms
        ):
            form.add_error(
                "origin",
                (
                    "Une action assignée doit avoir "
                    "au moins un destinataire."
                ),
            )
            return False

        return True

    def save_recipients(
        self,
        *,
        form,
        set_owner: bool,
    ):
        recipient_formset = self.get_recipient_formset(
            form=form,
        )

        formset_valid = recipient_formset.is_valid()

        if not (
            formset_valid
            and self.validate_business_rules(
                form=form,
                recipient_formset=recipient_formset,
            )
        ):
            return None

        with transaction.atomic():
            action = form.save(commit=False)

            if set_owner:
                action.owner = self.request.user
                action.status = TodoAction.Status.TODO

            action.full_clean()
            action.save()

            recipient_formset.instance = action
            recipient_formset.save()

        return action


class TodoActionCreateView(
    LoginRequiredMixin,
    TodoActionReturnUrlMixin,
    TodoActionFormsetMixin,
    EPCreateView,
):
    """
    Création d'une action Todo et de ses destinataires.
    """

    model = TodoAction
    form_class = TodoActionForm
    definition = TODO_ACTION_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def form_valid(self, form):
        action = self.save_recipients(
            form=form,
            set_owner=True,
        )

        if action is None:
            messages.error(
                self.request,
                "Certaines informations sont incorrectes.",
            )

            return self.render_to_response(
                self.get_context_data(form=form)
            )

        self.object = action

        messages.success(
            self.request,
            "L'action a été créée.",
        )

        return redirect(self.get_success_url())


class TodoActionUpdateView(
    LoginRequiredMixin,
    TodoActionReturnUrlMixin,
    TodoActionFormsetMixin,
    EPUpdateView,
):
    """
    Modification d'une action par son rédacteur.
    """

    model = TodoAction
    form_class = TodoActionForm
    definition = TODO_ACTION_FORM_DEFINITION
    template_name = "edf/form/view.html"

    def get_queryset(self):
        return TodoAction.objects.filter(
            owner=self.request.user,
        )

    def form_valid(self, form):
        action = self.save_recipients(
            form=form,
            set_owner=False,
        )

        if action is None:
            messages.error(
                self.request,
                "Certaines informations sont incorrectes.",
            )

            return self.render_to_response(
                self.get_context_data(form=form)
            )

        self.object = action

        messages.success(
            self.request,
            "L'action a été modifiée.",
        )

        return redirect(self.get_success_url())


class TodoActionDeleteView(
    LoginRequiredMixin,
    TodoActionReturnUrlMixin,
    View,
):
    """
    Suppression d'une action par son rédacteur.
    """

    def post(
        self,
        request,
        *,
        pk,
    ):
        action = get_object_or_404(
            TodoAction,
            pk=pk,
            owner=request.user,
        )

        title = action.title

        action.delete()

        messages.success(
            request,
            f'L’action "{title}" a été supprimée.',
        )

        return redirect(self.get_success_url())