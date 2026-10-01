

from __future__ import annotations

from framework.list import ListDefinition


class EPListSortingMixin:
    """
    Gestion générique du tri des listes Django.

    Les paramètres d'URL sont :
    - sort : identifiant de colonne ;
    - direction : asc ou desc.

    Seules les colonnes déclarées comme triables dans la
    ListDefinition peuvent être utilisées.
    """

    list_definition: ListDefinition | None = None

    sort_parameter = "sort"
    sort_direction_parameter = "direction"

    ascending_direction = "asc"
    descending_direction = "desc"

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

    def get_sort_by(self) -> str | None:
        """
        Retourne l'identifiant de la colonne de tri effective.
        """

        definition = self.get_list_definition()

        requested_identifier = (
            self.request.GET.get(
                self.sort_parameter,
                "",
            )
            .strip()
        )

        if not requested_identifier:
            return definition.default_sort

        if not definition.has_column(requested_identifier):
            return definition.default_sort

        column = definition.get_column(
            requested_identifier,
        )

        if not column.sortable:
            return definition.default_sort

        return requested_identifier

    def get_sort_descending(self) -> bool:
        """
        Indique si le tri effectif est décroissant.
        """

        return (
            self.request.GET.get(
                self.sort_direction_parameter,
                self.ascending_direction,
            )
            == self.descending_direction
        )

    def get_sort_field_map(self) -> dict[str, str]:
        """
        Retourne la correspondance entre colonnes et champs ORM.

        Une vue métier peut surcharger cette méthode lorsque le nom
        de la colonne diffère du champ ORM utilisé pour le tri.
        """

        definition = self.get_list_definition()

        return {
            column.identifier: column.field.name
            for column in definition.columns
            if column.sortable
        }

    def get_sort_field(self) -> str | None:
        """
        Retourne le champ ORM correspondant au tri effectif.
        """

        sort_by = self.get_sort_by()

        if sort_by is None:
            return None

        return self.get_sort_field_map().get(sort_by)

    def get_queryset(self):
        """
        Applique le tri avant la pagination Django.
        """

        queryset = super().get_queryset()

        sort_field = self.get_sort_field()

        if sort_field is None:
            return queryset

        ordering = (
            f"-{sort_field}"
            if self.get_sort_descending()
            else sort_field
        )

        return queryset.order_by(
            ordering,
            "pk",
        )