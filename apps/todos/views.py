

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from framework.integrations.django.list_pagination import (
    EPListPaginationMixin,
)
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
from .lists import TODO_LIST_DEFINITION
from .models import TodoAction
from .selectors import get_user_todo_actions


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

        return context


class TodoActionCreateView(
    LoginRequiredMixin,
    View,
):
    """
    Création d'une action Todo et de ses éventuels
    destinataires dans une transaction unique.
    """

    template_name = (
        "todos/todo_action_form.html"
    )

    def get(self, request):
        action = TodoAction(
            owner=request.user,
            origin=TodoAction.Origin.PERSONAL,
        )

        form = TodoActionForm(
            instance=action,
        )

        recipient_formset = (
            TodoActionRecipientFormSet(
                instance=action,
                prefix="recipients",
            )
        )

        return self._render(
            request=request,
            form=form,
            recipient_formset=recipient_formset,
        )

    def post(self, request):
        action = TodoAction(
            owner=request.user,
        )

        form = TodoActionForm(
            request.POST,
            instance=action,
        )

        recipient_formset = (
            TodoActionRecipientFormSet(
                request.POST,
                instance=action,
                prefix="recipients",
            )
        )

        form_valid = form.is_valid()
        formset_valid = recipient_formset.is_valid()

        if (
            form_valid
            and formset_valid
            and self._validate_business_rules(
                form=form,
                recipient_formset=recipient_formset,
            )
        ):
            with transaction.atomic():
                action = form.save(
                    commit=False
                )

                action.owner = request.user
                action.status = (
                    TodoAction.Status.TODO
                )

                action.full_clean()
                action.save()

                recipient_formset.instance = action
                recipient_formset.save()

            messages.success(
                request,
                "L'action a été créée.",
            )

            return redirect(
                "todos:list"
            )

        return self._render(
            request=request,
            form=form,
            recipient_formset=recipient_formset,
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
            if not hasattr(
                recipient_form,
                "cleaned_data",
            ):
                continue

            cleaned_data = (
                recipient_form.cleaned_data
            )

            if not cleaned_data:
                continue

            if cleaned_data.get(
                "DELETE"
            ):
                continue

            if cleaned_data.get(
                "user"
            ):
                active_recipient_forms.append(
                    recipient_form
                )

        if (
            origin
            == TodoAction.Origin.PERSONAL
            and active_recipient_forms
        ):
            form.add_error(
                "origin",
                (
                    "Une action personnelle ne peut "
                    "pas avoir de destinataire."
                ),
            )

            return False

        if (
            origin
            == TodoAction.Origin.ASSIGNED
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

    def _render(
        self,
        *,
        request,
        form,
        recipient_formset,
    ):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "recipient_formset": (
                    recipient_formset
                ),
            },
        )