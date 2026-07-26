

from django.contrib.auth.base_user import BaseUserManager

from .querysets import UserQuerySet


class UserManager(BaseUserManager.from_queryset(UserQuerySet)):
    """Manager du modèle User."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Méthode interne de création d'un utilisateur.
        """
        if not email:
            raise ValueError("L'adresse électronique est obligatoire.")

        email = self.normalize_email(email).strip().lower()

        user = self.model(
            email=email,
            **extra_fields,
        )

        user.set_password(password)
        user.full_clean()
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Création d'un utilisateur standard.
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )

    def create_superuser(self, email, password, **extra_fields):
        """
        Création d'un superutilisateur.
        """
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self._create_user(
            email=email,
            password=password,
            **extra_fields,
        )