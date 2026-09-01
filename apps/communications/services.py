

from __future__ import annotations

from collections.abc import (
    Iterable,
    Mapping,
)

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessage,
    CommunicationMessageRecipient,
)
from apps.projects.models import (
    ProjectExternalParticipant,
    ProjectMembership,
)
from apps.users.models import User


class CommunicationService:
    """
    Services métier du domaine Communications.

    Un message constitue une communication unique.

    Ses destinataires sont portés par des distributions
    indépendantes pouvant utiliser différents canaux :

    - INTERNAL : utilisateur Easy Projet ;
    - EMAIL : intervenant externe ;
    - MOBILE : usage futur.

    Chaque distribution précise également si le message
    est adressé pour action ou pour information.
    """

    # ==================================================================
    # Envoi mixte
    # ==================================================================

    @classmethod
    @transaction.atomic
    def send_project_message(
        cls,
        *,
        conversation: CommunicationConversation,
        author: User,
        body: str,
        internal_recipients: Iterable[User] = (),
        external_recipients: Iterable[
            ProjectExternalParticipant
        ] = (),
        subject: str = "",
        recipient_purposes: Mapping[
            str,
            str,
        ] | None = None,
    ) -> CommunicationMessage:
        """
        Crée une communication projet unique pouvant être
        distribuée à des destinataires internes et externes.

        recipient_purposes utilise comme clé l'identifiant
        du destinataire.

        Exemple :

            {
                str(user.pk): "ACTION",
                str(external.pk): "INFORMATION",
            }

        Les destinataires internes donnent lieu à une
        distribution INTERNAL.

        Les intervenants externes donnent lieu à une
        distribution EMAIL.

        L'envoi SMTP n'est pas encore effectué.
        """

        internal_list = cls._unique_users(
            internal_recipients
        )

        external_list = (
            cls._unique_external_participants(
                external_recipients
            )
        )

        cls._validate_body(
            body
        )

        cls._validate_at_least_one_recipient(
            internal_recipients=internal_list,
            external_recipients=external_list,
        )

        if internal_list:
            cls._validate_internal_recipients(
                conversation=conversation,
                recipients=internal_list,
            )

        if external_list:
            cls._validate_external_recipients(
                conversation=conversation,
                recipients=external_list,
            )

        message = CommunicationMessage(
            conversation=conversation,
            origin=(
                CommunicationMessage
                .Origin
                .INTERNAL
            ),
            author=author,
            subject=(
                subject
                or ""
            ).strip(),
            body=body.strip(),
        )

        message.full_clean()
        message.save()

        cls._create_internal_distributions(
            message=message,
            recipients=internal_list,
            recipient_purposes=(
                recipient_purposes
            ),
        )

        cls._create_external_distributions(
            message=message,
            recipients=external_list,
            recipient_purposes=(
                recipient_purposes
            ),
        )

        return message

    # ==================================================================
    # Façades de compatibilité
    # ==================================================================

    @classmethod
    @transaction.atomic
    def send_internal_message(
        cls,
        *,
        conversation: CommunicationConversation,
        author: User,
        body: str,
        recipients: Iterable[User],
        subject: str = "",
        recipient_purposes: Mapping[
            str,
            str,
        ] | None = None,
    ) -> CommunicationMessage:
        """
        Crée une communication destinée uniquement
        à des utilisateurs Easy Projet.

        Cette méthode reste disponible pour compatibilité
        avec les usages existants.
        """

        return cls.send_project_message(
            conversation=conversation,
            author=author,
            subject=subject,
            body=body,
            internal_recipients=recipients,
            recipient_purposes=(
                recipient_purposes
            ),
        )

    @classmethod
    @transaction.atomic
    def send_email_message(
        cls,
        *,
        conversation: CommunicationConversation,
        author: User,
        body: str,
        recipients: Iterable[
            ProjectExternalParticipant
        ],
        subject: str = "",
        recipient_purposes: Mapping[
            str,
            str,
        ] | None = None,
    ) -> CommunicationMessage:
        """
        Crée une communication destinée uniquement
        à des intervenants externes par email.

        Cette méthode prépare les distributions EMAIL.
        L'envoi SMTP n'est pas encore effectué.

        Elle reste disponible pour compatibilité avec
        les usages existants.
        """

        return cls.send_project_message(
            conversation=conversation,
            author=author,
            subject=subject,
            body=body,
            external_recipients=recipients,
            recipient_purposes=(
                recipient_purposes
            ),
        )

    # ==================================================================
    # Création des distributions
    # ==================================================================

    @classmethod
    def _create_internal_distributions(
        cls,
        *,
        message: CommunicationMessage,
        recipients: list[User],
        recipient_purposes: Mapping[
            str,
            str,
        ] | None,
    ) -> None:
        """
        Crée les distributions de messagerie interne.
        """

        for recipient in recipients:

            purpose = cls._get_recipient_purpose(
                recipient_id=str(
                    recipient.pk
                ),
                recipient_purposes=(
                    recipient_purposes
                ),
            )

            distribution = (
                CommunicationMessageRecipient(
                    message=message,
                    user=recipient,
                    purpose=purpose,
                    channel=(
                        CommunicationMessageRecipient
                        .Channel
                        .INTERNAL
                    ),
                )
            )

            distribution.full_clean()
            distribution.save()

    @classmethod
    def _create_external_distributions(
        cls,
        *,
        message: CommunicationMessage,
        recipients: list[
            ProjectExternalParticipant
        ],
        recipient_purposes: Mapping[
            str,
            str,
        ] | None,
    ) -> None:
        """
        Crée les distributions email destinées
        aux intervenants externes.
        """

        for recipient in recipients:

            purpose = cls._get_recipient_purpose(
                recipient_id=str(
                    recipient.pk
                ),
                recipient_purposes=(
                    recipient_purposes
                ),
            )

            distribution = (
                CommunicationMessageRecipient(
                    message=message,
                    external_participant=recipient,
                    destination_email=(
                        recipient.email
                    ),
                    purpose=purpose,
                    channel=(
                        CommunicationMessageRecipient
                        .Channel
                        .EMAIL
                    ),
                )
            )

            distribution.full_clean()
            distribution.save()

    # ==================================================================
    # Validation
    # ==================================================================

    @staticmethod
    def _validate_body(
        body: str,
    ) -> None:
        """
        Un message utilisateur ne peut pas être vide.
        """

        if not isinstance(
            body,
            str,
        ):
            raise ValidationError(
                {
                    "body": (
                        "Le contenu du message "
                        "doit être une chaîne de caractères."
                    ),
                }
            )

        if not body.strip():
            raise ValidationError(
                {
                    "body": (
                        "Le message ne peut pas être vide."
                    ),
                }
            )

    @staticmethod
    def _validate_at_least_one_recipient(
        *,
        internal_recipients: list[User],
        external_recipients: list[
            ProjectExternalParticipant
        ],
    ) -> None:
        """
        Une communication doit posséder au moins
        un destinataire, quel que soit son canal.
        """

        if (
            not internal_recipients
            and not external_recipients
        ):
            raise ValidationError(
                {
                    "recipients": (
                        "Au moins un destinataire "
                        "doit être renseigné."
                    ),
                }
            )

    @staticmethod
    def _validate_internal_recipients(
        *,
        conversation: CommunicationConversation,
        recipients: list[User],
    ) -> None:
        """
        Vérifie les destinataires internes.

        Chaque utilisateur doit :
        - être actif ;
        - disposer d'une affectation active au projet.
        """

        project_id = (
            conversation.project_id
        )

        recipient_ids = [
            recipient.pk
            for recipient in recipients
        ]

        valid_user_ids = set(
            ProjectMembership.objects
            .filter(
                project_id=project_id,
                user_id__in=recipient_ids,
                user__is_active=True,
                is_active=True,
            )
            .values_list(
                "user_id",
                flat=True,
            )
        )

        invalid_recipients = [
            recipient
            for recipient in recipients
            if recipient.pk
            not in valid_user_ids
        ]

        if invalid_recipients:
            raise ValidationError(
                {
                    "recipients": (
                        "Tous les destinataires internes "
                        "doivent être des utilisateurs actifs "
                        "affectés au projet."
                    ),
                }
            )

    @staticmethod
    def _validate_external_recipients(
        *,
        conversation: CommunicationConversation,
        recipients: list[
            ProjectExternalParticipant
        ],
    ) -> None:
        """
        Vérifie les destinataires externes.

        Chaque intervenant doit :
        - appartenir au projet ;
        - être actif ;
        - disposer d'une adresse email.
        """

        for recipient in recipients:

            if (
                recipient.project_id
                != conversation.project_id
            ):
                raise ValidationError(
                    {
                        "recipients": (
                            "Tous les intervenants externes "
                            "doivent appartenir au projet."
                        ),
                    }
                )

            if not recipient.is_active:
                raise ValidationError(
                    {
                        "recipients": (
                            "Un intervenant externe inactif "
                            "ne peut pas être destinataire."
                        ),
                    }
                )

            if not recipient.email:
                raise ValidationError(
                    {
                        "recipients": (
                            "Chaque intervenant externe "
                            "doit disposer d'une adresse email."
                        ),
                    }
                )

    # ==================================================================
    # Rôle de diffusion
    # ==================================================================

    @staticmethod
    def _get_recipient_purpose(
        *,
        recipient_id: str,
        recipient_purposes: Mapping[
            str,
            str,
        ] | None,
    ) -> str:
        """
        Retourne le rôle de diffusion d'un destinataire.

        INFORMATION constitue la valeur par défaut.
        """

        purpose = (
            CommunicationMessageRecipient
            .Purpose
            .INFORMATION
        )

        if recipient_purposes is not None:
            purpose = recipient_purposes.get(
                recipient_id,
                purpose,
            )

        valid_purposes = {
            value
            for value, _label
            in (
                CommunicationMessageRecipient
                .Purpose
                .choices
            )
        }

        if purpose not in valid_purposes:
            raise ValidationError(
                {
                    "purpose": (
                        "Le type de diffusion doit être "
                        "'Pour action' ou "
                        "'Pour information'."
                    ),
                }
            )

        return purpose

    # ==================================================================
    # Normalisation des destinataires
    # ==================================================================

    @staticmethod
    def _unique_users(
        recipients: Iterable[User],
    ) -> list[User]:
        """
        Supprime les doublons tout en conservant
        l'ordre initial.
        """

        result = []
        seen = set()

        for recipient in recipients:

            if recipient.pk in seen:
                continue

            seen.add(
                recipient.pk
            )

            result.append(
                recipient
            )

        return result

    @staticmethod
    def _unique_external_participants(
        recipients: Iterable[
            ProjectExternalParticipant
        ],
    ) -> list[
        ProjectExternalParticipant
    ]:
        """
        Supprime les doublons tout en conservant
        l'ordre initial.
        """

        result = []
        seen = set()

        for recipient in recipients:

            if recipient.pk in seen:
                continue

            seen.add(
                recipient.pk
            )

            result.append(
                recipient
            )

        return result