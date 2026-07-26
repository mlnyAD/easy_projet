

from django.db import models


class UserQuerySet(models.QuerySet):
    """Requêtes spécifiques aux utilisateurs."""

    def active(self):
        """Utilisateurs actifs."""
        return self.filter(is_active=True)

    def inactive(self):
        """Utilisateurs inactifs."""
        return self.filter(is_active=False)

    def for_company(self, company):
        """Utilisateurs d'une société."""
        return self.filter(company=company)

    def with_global_role(self, role):
        """Utilisateurs ayant un rôle global."""
        return self.filter(global_role=role)

    def with_access_level(self, level):
        """Utilisateurs ayant un niveau d'accès."""
        return self.filter(access_level=level)

    def search(self, value):
        """
        Recherche simple sur l'identité ou l'adresse électronique.
        """
        value = (value or "").strip()

        if not value:
            return self

        return self.filter(
            models.Q(first_name__icontains=value)
            | models.Q(last_name__icontains=value)
            | models.Q(preferred_name__icontains=value)
            | models.Q(email__icontains=value)
        )