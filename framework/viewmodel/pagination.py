

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PaginationViewModel:
    """Représente les informations de pagination utiles à une vue."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    previous_page: int | None
    next_page: int | None

    def __post_init__(self) -> None:
        self._validate_positive_integer(
            self.page,
            property_name="page",
        )
        self._validate_positive_integer(
            self.page_size,
            property_name="page_size",
        )
        self._validate_non_negative_integer(
            self.total_items,
            property_name="total_items",
        )
        self._validate_non_negative_integer(
            self.total_pages,
            property_name="total_pages",
        )

        if not isinstance(self.has_previous, bool):
            raise TypeError(
                "La propriété 'has_previous' doit être un booléen."
            )

        if not isinstance(self.has_next, bool):
            raise TypeError(
                "La propriété 'has_next' doit être un booléen."
            )

        self._validate_optional_positive_integer(
            self.previous_page,
            property_name="previous_page",
        )
        self._validate_optional_positive_integer(
            self.next_page,
            property_name="next_page",
        )

        if self.has_previous != (self.previous_page is not None):
            raise ValueError(
                "'has_previous' et 'previous_page' sont incohérents."
            )

        if self.has_next != (self.next_page is not None):
            raise ValueError(
                "'has_next' et 'next_page' sont incohérents."
            )

        if (
            self.previous_page is not None
            and self.previous_page != self.page - 1
        ):
            raise ValueError(
                "'previous_page' doit désigner la page précédente."
            )

        if (
            self.next_page is not None
            and self.next_page != self.page + 1
        ):
            raise ValueError(
                "'next_page' doit désigner la page suivante."
            )
            
    @property
    def first_item(self) -> int:
        """Retourne le rang du premier élément affiché."""

        if self.total_items == 0:
            return 0

        return ((self.page - 1) * self.page_size) + 1


    @property
    def last_item(self) -> int:
        """Retourne le rang du dernier élément affiché."""

        if self.total_items == 0:
            return 0

        return min(
            self.page * self.page_size,
            self.total_items,
        )

    def _validate_positive_integer(
        self,
        value: object,
        *,
        property_name: str,
    ) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"La propriété {property_name!r} doit être un entier."
            )

        if value <= 0:
            raise ValueError(
                f"La propriété {property_name!r} "
                "doit être strictement positive."
            )

    def _validate_non_negative_integer(
        self,
        value: object,
        *,
        property_name: str,
    ) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(
                f"La propriété {property_name!r} doit être un entier."
            )

        if value < 0:
            raise ValueError(
                f"La propriété {property_name!r} "
                "ne peut pas être négative."
            )

    def _validate_optional_positive_integer(
        self,
        value: object,
        *,
        property_name: str,
    ) -> None:
        if value is None:
            return

        self._validate_positive_integer(
            value,
            property_name=property_name,
        )