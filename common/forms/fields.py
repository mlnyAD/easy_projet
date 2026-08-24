

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue


class CatalogModelChoiceField(forms.ModelChoiceField):
    """
    Champ de sélection d'une valeur de catalogue.

    Le champ conserve également les propriétés nécessaires au rendu
    contextuel du catalogue.
    """

    def __init__(
        self,
        *args,
        catalog_code: str,
        catalog_is_editable: bool = False,
        catalog_is_incremental: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.catalog_code = catalog_code
        self.catalog_is_editable = catalog_is_editable
        self.catalog_is_incremental = catalog_is_incremental

    @property
    def allows_catalog_increment(self) -> bool:
        """
        Indique si l'utilisateur peut ajouter
        une nouvelle valeur au catalogue.
        """

        return (
            self.catalog_is_editable
            and self.catalog_is_incremental
            and not self.disabled
        )

    def label_from_instance(
        self,
        obj: CatalogValue,
    ) -> str:
        return obj.label