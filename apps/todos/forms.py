

from __future__ import annotations

from django import forms
from django.forms import inlineformset_factory

from apps.todos.models import (
    TodoAction,
    TodoActionRecipient,
)
from apps.users.models import User


class TodoActionForm(forms.ModelForm):
    """
    Formulaire principal d'une action Todo.

    Le propriétaire et l'état initial sont gérés
    par l'application et non saisis par l'utilisateur.
    """

    due_date = forms.DateField(
        label="Date de fin",
        required=False,
        input_formats=[
            "%Y-%m-%d",
        ],
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={
                "type": "date",
            },
        ),
    )

    class Meta:
        model = TodoAction

        fields = (
            "title",
            "details",
            "due_date",
            "origin",
            "project",
        )
        labels = {
            "origin": "Affectation",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                }
            ),
            "details": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
        }


class TodoActionRecipientForm(forms.ModelForm):
    """
    Destinataire d'une action assignée.
    """

    class Meta:
        model = TodoActionRecipient

        fields = (
            "user",
            "role",
        )


TodoActionRecipientFormSet = inlineformset_factory(
    TodoAction,
    TodoActionRecipient,
    form=TodoActionRecipientForm,
    extra=1,
    can_delete=True,
)