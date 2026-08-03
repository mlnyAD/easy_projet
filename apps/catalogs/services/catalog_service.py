

from __future__ import annotations

from django.db import transaction

from apps.catalogs import selectors
from apps.catalogs.exceptions import (
    CatalogInactiveError,
    CatalogNotEditableError,
    CatalogNotIncrementalError,
    CatalogValueAlreadyExistsError,
    CatalogValueInactiveError,
)
from apps.catalogs.models import CatalogType, CatalogValue


class CatalogService:
    """Point d'entrée public du domaine des catalogues."""

    @staticmethod
    def _get_active_catalog(
        catalog_code: str,
    ) -> CatalogType:
        normalized_code = catalog_code.strip().upper()

        catalog = selectors.get_catalog_by_code(
            normalized_code,
        )

        if not catalog.is_active:
            raise CatalogInactiveError(normalized_code)

        return catalog

    @staticmethod
    def _check_catalog_can_be_updated(
        catalog: CatalogType,
    ) -> None:
        if not catalog.is_editable:
            raise CatalogNotEditableError(catalog.code)

        if not catalog.is_incremental:
            raise CatalogNotIncrementalError(catalog.code)

    @staticmethod
    def _unset_current_default(
        catalog: CatalogType,
    ) -> None:
        current_default = selectors.get_default_catalog_value(
            catalog,
            active_only=False,
        )

        if current_default is None:
            return

        current_default.is_default = False
        current_default.full_clean()
        current_default.save(
            update_fields=[
                "is_default",
                "updated_at",
            ],
        )

    @staticmethod
    def get_values(
        catalog_code: str,
    ) -> list[CatalogValue]:
        catalog = CatalogService._get_active_catalog(
            catalog_code,
        )

        return list(
            selectors.list_catalog_values(
                catalog,
                active_only=True,
            )
        )

    @staticmethod
    def get_choices(
        catalog_code: str,
    ) -> list[tuple[str, str]]:
        """
        Retourne les valeurs actives d'un catalogue au format attendu
        par les champs Django.

        Retourne une liste vide si le catalogue n'existe pas
        ou s'il est inactif.
        """
        normalized_code = catalog_code.strip().upper()

        queryset = (
            CatalogValue.objects
            .filter(
                catalog_type__code=normalized_code,
                catalog_type__is_active=True,
                is_active=True,
            )
            .order_by(
                "level",
                "sort_order",
                "label",
            )
        )

        return [
            (
                str(value.pk),
                value.label,
            )
            for value in queryset
        ]
    
    @staticmethod
    def get_value(
        catalog_code: str,
        value_code: str,
    ) -> CatalogValue:
        catalog = CatalogService._get_active_catalog(
            catalog_code,
        )

        value = selectors.get_catalog_value_by_code(
            catalog,
            value_code.strip().upper(),
        )

        if not value.is_active:
            raise CatalogValueInactiveError(
                catalog.code,
                value.code,
            )

        return value

    @staticmethod
    def get_default_value(
        catalog_code: str,
    ) -> CatalogValue | None:
        catalog = CatalogService._get_active_catalog(
            catalog_code,
        )

        return selectors.get_default_catalog_value(
            catalog,
        )

    @staticmethod
    def has_value(
        catalog_code: str,
        value_code: str,
    ) -> bool:
        catalog = CatalogService._get_active_catalog(
            catalog_code,
        )

        return selectors.catalog_value_exists(
            catalog,
            value_code.strip().upper(),
            active_only=True,
        )

    @staticmethod
    @transaction.atomic
    def create_value(
        catalog_code: str,
        code: str,
        label: str,
        *,
        description: str = "",
        sort_order: int | None = None,
        is_default: bool = False,
        is_system: bool = False,
        is_active: bool = True,
    ) -> CatalogValue:
        """
        Crée une valeur dans un catalogue actif, modifiable
        et incrémental.
        """
        catalog = CatalogService._get_active_catalog(
            catalog_code,
        )

        CatalogService._check_catalog_can_be_updated(
            catalog,
        )

        normalized_code = code.strip().upper()
        normalized_label = label.strip()

        if selectors.catalog_value_exists(
            catalog,
            normalized_code,
            active_only=False,
        ):
            raise CatalogValueAlreadyExistsError(
                catalog.code,
                normalized_code,
            )

        if sort_order is None:
            sort_order = selectors.get_next_sort_order(
                catalog,
            )

        if is_default:
            CatalogService._unset_current_default(
                catalog,
            )

        value = CatalogValue(
            catalog_type=catalog,
            code=normalized_code,
            label=normalized_label,
            description=description.strip(),
            sort_order=sort_order,
            is_default=is_default,
            is_system=is_system,
            is_active=is_active,
        )

        value.full_clean()
        value.save()

        return value

    @staticmethod
    @transaction.atomic
    def upsert_type(
        code: str,
        label: str,
        *,
        description: str = "",
        is_hierarchical: bool = False,
        is_editable: bool = False,
        is_incremental: bool = False,
        is_active: bool = True,
    ) -> CatalogType:
        catalog, _created = CatalogType.objects.update_or_create(
            code=code.strip().upper(),
            defaults={
                "label": label.strip(),
                "description": description.strip(),
                "is_hierarchical": is_hierarchical,
                "is_editable": is_editable,
                "is_incremental": is_incremental,
                "is_active": is_active,
            },
        )

        catalog.full_clean()
        catalog.save()

        return catalog

    @staticmethod
    @transaction.atomic
    def upsert_value(
        catalog_code: str,
        code: str,
        label: str,
        *,
        description: str = "",
        parent_code: str | None = None,
        sort_order: int = 10,
        is_default: bool = False,
        is_system: bool = True,
        is_active: bool = True,
    ) -> CatalogValue:
        catalog = selectors.get_catalog_by_code(
            catalog_code.strip().upper(),
        )

        parent = None

        if parent_code is not None:
            parent = selectors.get_catalog_value_by_code(
                catalog,
                parent_code.strip().upper(),
            )

        value, _created = CatalogValue.objects.update_or_create(
            catalog_type=catalog,
            code=code.strip().upper(),
            defaults={
                "label": label.strip(),
                "description": description.strip(),
                "parent": parent,
                "sort_order": sort_order,
                "is_default": is_default,
                "is_system": is_system,
                "is_active": is_active,
            },
        )

        value.full_clean()
        value.save()

        return value