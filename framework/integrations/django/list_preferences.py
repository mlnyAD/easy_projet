

from __future__ import annotations

from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.shortcuts import redirect

from apps.users.services.list_preference import (
    UserListPreferenceService,
)
from framework.list import ListDefinition


class EPListPreferencesMixin:
    """
    Gestion générique des colonnes visibles d'une liste.

    Une requête GET lit les préférences de l'utilisateur connecté.
    Une requête POST enregistre la sélection reçue dans le paramètre
    ``visible_columns`` puis revient sur la même liste.
    """

    list_definition: ListDefinition | None = None

    visible_columns_parameter = "visible_columns"

    def get_list_definition(self) -> ListDefinition:
        """
        Retourne la définition associée à la vue de liste.
        """

        definition = self.list_definition

        if not isinstance(
            definition,
            ListDefinition,
        ):
            raise TypeError(
                "La vue doit définir une propriété "
                "'list_definition' de type ListDefinition."
            )

        return definition

    def get_visible_column_identifiers(
        self,
    ) -> tuple[str, ...]:
        """
        Retourne les colonnes à afficher pour la requête courante.
        """

        definition = self.get_list_definition()

        user = self.request.user

        if not user.is_authenticated:
            return tuple(
                column.identifier
                for column in definition.visible_columns
            )

        return (
            UserListPreferenceService
            .get_visible_column_identifiers(
                user=user,
                definition=definition,
            )
        )

    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Enregistre le choix de colonnes de l'utilisateur.
        """

        if not request.user.is_authenticated:
            return HttpResponseForbidden(
                "Vous devez être authentifié pour enregistrer "
                "vos préférences de liste."
            )

        definition = self.get_list_definition()

        identifiers = request.POST.getlist(
            self.visible_columns_parameter,
        )

        try:
            UserListPreferenceService.save_visible_column_identifiers(
                user=request.user,
                definition=definition,
                identifiers=identifiers,
            )
        except (TypeError, ValueError) as error:
            return HttpResponseBadRequest(str(error))

        return redirect(request.get_full_path())