

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
    """
    Point d'entrée public du domaine des catalogues.

    Les vues, formulaires et autres domaines doivent utiliser ce service
    plutôt que d'accéder directement aux selectors ou aux modèles.
    """

    @staticmethod
    def _get_active_catalog(
        catalog_code: str,
    ) -> CatalogType:
        """
        Retourne un catalogue actif.

        Lève CatalogNotFoundError si le catalogue n'existe pas.
        Lève CatalogInactiveError si le catalogue est inactif.
        """
        catalog = selectors.get_catalog_by_code(catalog_code)

        if not catalog.is_active:
            raise CatalogInactiveError(catalog_code)

        return catalog

    @staticmethod
    def _check_catalog_can_be_updated(
        catalog: CatalogType,
    ) -> None:
        """
        Vérifie que le catalogue autorise les écritures.
        """
        if not catalog.is_editable:
            raise CatalogNotEditableError(catalog.code)

        if not catalog.is_incremental:
            raise CatalogNotIncrementalError(catalog.code)
        
        
    @staticmethod
    def _unset_current_default(
        catalog: CatalogType,
    ) -> None:
        """
        Retire le statut de valeur par défaut à la valeur actuelle,
        si le catalogue en possède une.
        """
        current_default = selectors.get_default_catalog_value(
            catalog,
            active_only=False,
        )

        if current_default is None:
            return

        current_default.is_default = False
        current_default.full_clean()
        current_default.save()	
        

    @staticmethod
    def get_values(
        catalog_code: str,
    ) -> list[CatalogValue]:
        """
        Retourne les valeurs actives d'un catalogue.
        """
        catalog = CatalogService._get_active_catalog(catalog_code)

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
        Retourne les valeurs actives sous forme de choix Django.
        """
        values = CatalogService.get_values(catalog_code)

        return [
            (value.code, value.label)
            for value in values
        ]

    @staticmethod
    def get_value(
        catalog_code: str,
        value_code: str,
    ) -> CatalogValue:
        """
        Retourne une valeur active d'un catalogue.

        Lève CatalogValueNotFoundError si la valeur n'existe pas.
        Lève CatalogValueInactiveError si elle est inactive.
        """
        catalog = CatalogService._get_active_catalog(catalog_code)

        value = selectors.get_catalog_value_by_code(
            catalog,
            value_code,
        )

        if not value.is_active:
            raise CatalogValueInactiveError(
                catalog_code,
                value_code,
            )

        return value

    @staticmethod
    def get_default_value(
        catalog_code: str,
    ) -> CatalogValue | None:
        """
        Retourne la valeur active définie par défaut.

        Retourne None si aucune valeur par défaut active n'est définie.
        """
        catalog = CatalogService._get_active_catalog(catalog_code)

        return selectors.get_default_catalog_value(catalog)

    @staticmethod
    def has_value(
        catalog_code: str,
        value_code: str,
    ) -> bool:
        """
        Indique si une valeur active existe dans un catalogue.
        """
        catalog = CatalogService._get_active_catalog(catalog_code)

        return selectors.catalog_value_exists(
            catalog,
            value_code,
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
        Prépare la création d'une nouvelle valeur de catalogue.

        L'implémentation complète de la persistance sera ajoutée
        après validation de cette première structure.
        """
        catalog = CatalogService._get_active_catalog(catalog_code)

        CatalogService._check_catalog_can_be_updated(catalog)

        if selectors.catalog_value_exists(
            catalog,
            code,
            active_only=False,
        ):
            raise CatalogValueAlreadyExistsError(
                catalog_code,
                code,
            )

        if sort_order is None:
            sort_order = selectors.get_next_sort_order(catalog)

        if is_default:
            CatalogService._unset_current_default(catalog)

        value = CatalogValue(
            catalog_type=catalog,
            code=code,
            label=label,
            description=description,
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
            code=code,
            defaults={
                "label": label,
                "description": description,
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
        catalog = selectors.get_catalog_by_code(catalog_code)

        parent = None

        if parent_code is not None:
            parent = selectors.get_catalog_value_by_code(
                catalog,
                parent_code,
            )

        value, _created = CatalogValue.objects.update_or_create(
            catalog_type=catalog,
            code=code,
            defaults={
                "label": label,
                "description": description,
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