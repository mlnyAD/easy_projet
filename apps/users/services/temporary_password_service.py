

from __future__ import annotations

import secrets
import string

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from apps.users.models import User


class TemporaryPasswordService:
    """
    Gestion des mots de passe provisoires utilisateur.

    Le mot de passe provisoire :
    - est généré aléatoirement ;
    - n'est jamais stocké en clair ;
    - remplace immédiatement l'ancien mot de passe ;
    - impose un changement lors de la prochaine connexion ;
    - est envoyé à l'utilisateur par email.
    """

    PASSWORD_LENGTH = 12

    SYMBOLS = "!@#$%*-_=+"

    @classmethod
    def generate_password(cls) -> str:
        """
        Génère un mot de passe provisoire robuste.

        Le mot de passe contient au minimum :
        - une lettre minuscule ;
        - une lettre majuscule ;
        - un chiffre ;
        - un caractère spécial.
        """

        characters = (
            string.ascii_letters
            + string.digits
            + cls.SYMBOLS
        )

        password_characters = [
            secrets.choice(
                string.ascii_lowercase
            ),
            secrets.choice(
                string.ascii_uppercase
            ),
            secrets.choice(
                string.digits
            ),
            secrets.choice(
                cls.SYMBOLS
            ),
        ]

        password_characters.extend(
            secrets.choice(
                characters
            )
            for _ in range(
                cls.PASSWORD_LENGTH
                - len(password_characters)
            )
        )

        secrets.SystemRandom().shuffle(
            password_characters
        )

        return "".join(
            password_characters
        )

    @classmethod
    @transaction.atomic
    def reset_and_send(
        cls,
        *,
        user: User,
    ) -> None:
        """
        Génère et envoie un nouveau mot de passe provisoire.

        L'ancien mot de passe devient immédiatement invalide.

        En cas d'échec de l'envoi SMTP, la modification
        utilisateur est annulée par la transaction.
        """

        if not user.is_active:
            raise ValueError(
                "Un mot de passe provisoire ne peut pas "
                "être envoyé à un utilisateur inactif."
            )

        email = (
            user.email
            or ""
        ).strip().lower()

        if not email:
            raise ValueError(
                "L'utilisateur doit disposer "
                "d'une adresse électronique."
            )

        temporary_password = (
            cls.generate_password()
        )
        
        if settings.DEBUG:
            print(
                "\n"
                "========================================\n"
                "EASY PROJET - MOT DE PASSE PROVISOIRE\n"
                f"Utilisateur : {user.email}\n"
                f"Mot de passe : {temporary_password}\n"
                "========================================\n"
            )
            
        user.set_password(
            temporary_password
        )

        user.must_change_password = True

        user.temporary_password_sent_at = (
            timezone.now()
        )

        user.save(
            update_fields=[
                "password",
                "must_change_password",
                "temporary_password_sent_at",
                "updated_at",
            ]
        )

        cls._send_email(
            user=user,
            temporary_password=temporary_password,
        )

    @staticmethod
    def _send_email(
        *,
        user: User,
        temporary_password: str,
    ) -> None:
        """
        Envoie le mot de passe provisoire à l'utilisateur.
        """

        email = EmailMessage(
            subject=(
                "Easy Projet - "
                "Votre mot de passe provisoire"
            ),
            body=(
                f"Bonjour {user.first_name},\n\n"
                "Votre accès à Easy Projet a été préparé.\n\n"
                "Identifiant : "
                f"{user.email}\n"
                "Mot de passe provisoire : "
                f"{temporary_password}\n\n"
                "Lors de votre prochaine connexion, "
                "vous devrez définir votre mot de passe "
                "personnel.\n\n"
                "Cordialement,\n"
                "Easy Projet"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[
                user.email,
            ],
        )

        sent_count = email.send(
            fail_silently=False,
        )

        if sent_count != 1:
            raise RuntimeError(
                "Le serveur de messagerie "
                "n'a pas confirmé l'envoi "
                "du mot de passe provisoire."
            )