

class LicenseError(Exception):
    """Classe de base des erreurs du domaine des licences."""


class LicenseReferenceAlreadyExistsError(LicenseError):
    """
    Une licence portant cette référence existe déjà
    dans l'environnement client.
    """

    def __init__(self, reference: str) -> None:
        self.reference = reference

        super().__init__(
            f"Une licence portant la référence "
            f"'{reference}' existe déjà."
        )


class LicenseDateError(LicenseError):
    """Les dates de la licence sont incohérentes."""

    def __init__(self) -> None:
        super().__init__(
            "La date d'expiration ne peut pas être "
            "antérieure à la date d'attribution."
        )