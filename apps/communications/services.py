from __future__ import annotations

from collections.abc import Iterable, Mapping

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessage,
    CommunicationMessageRecipient,
)
from apps.projects.models import Project, ProjectExternalParticipant
from apps.users.models import User


class CommunicationService:
    """Création des messages et de leurs distributions."""

    @classmethod
    @transaction.atomic
    def send_message(
        cls,
        *,
        conversation: CommunicationConversation,
        author: User,
        body: str,
        internal_recipients: Iterable[User] = (),
        external_recipients: Iterable[ProjectExternalParticipant] = (),
        direct_email_recipients: Iterable[str] = (),
        subject: str = "",
        recipient_purposes: Mapping[str, str] | None = None,
    ) -> CommunicationMessage:
        internal = cls._unique_users(internal_recipients)
        external = cls._unique_external_participants(external_recipients)
        direct_emails = cls._unique_email_addresses(direct_email_recipients)
        cls._validate_body(body)
        cls._validate_recipients(
            internal=internal,
            external=external,
            direct_emails=direct_emails,
        )
        cls._validate_internal_recipients(author=author, recipients=internal)
        cls._validate_external_recipients(
            conversation=conversation,
            recipients=external,
        )

        message = CommunicationMessage(
            conversation=conversation,
            origin=CommunicationMessage.Origin.INTERNAL,
            author=author,
            subject=(subject or "").strip(),
            body=body.strip(),
        )
        message.full_clean()
        message.save()
        cls._create_internal_distributions(message, internal, recipient_purposes)
        cls._create_external_distributions(message, external, recipient_purposes)
        cls._create_direct_email_distributions(message, direct_emails, recipient_purposes)
        return message

    @classmethod
    @transaction.atomic
    def create_conversation(
        cls,
        *,
        author: User,
        title: str,
        projects: Iterable[Project] = (),
    ) -> CommunicationConversation:
        conversation = CommunicationConversation(
            title=(title or "").strip(),
            created_by=author,
        )
        conversation.full_clean()
        conversation.save()
        project_list = list({project.pk: project for project in projects}.values())
        if project_list:
            conversation.projects.add(*project_list)
        return conversation

    @classmethod
    def send_project_message(cls, **kwargs) -> CommunicationMessage:
        """Façade conservée pour les appels existants."""
        return cls.send_message(**kwargs)

    @staticmethod
    def _validate_body(body: str) -> None:
        if not isinstance(body, str) or not body.strip():
            raise ValidationError({"body": "Le message ne peut pas être vide."})

    @staticmethod
    def _validate_recipients(*, internal, external, direct_emails) -> None:
        if not internal and not external and not direct_emails:
            raise ValidationError({"recipients": "Au moins un destinataire doit être renseigné."})

    @staticmethod
    def _validate_internal_recipients(*, author: User, recipients: list[User]) -> None:
        invalid = [
            recipient
            for recipient in recipients
            if not recipient.is_active or recipient.company_id != author.company_id
        ]
        if invalid:
            raise ValidationError({"recipients": "Les destinataires internes doivent être des utilisateurs actifs de la même société."})

    @staticmethod
    def _validate_external_recipients(*, conversation, recipients) -> None:
        project_ids = set(conversation.projects.values_list("pk", flat=True))
        for recipient in recipients:
            if not recipient.is_active or not recipient.email:
                raise ValidationError({"recipients": "Chaque intervenant externe doit être actif et avoir une adresse email."})
            if recipient.project_id not in project_ids:
                raise ValidationError({"recipients": "Un intervenant externe doit appartenir à un projet lié à la conversation."})

    @classmethod
    def _create_internal_distributions(cls, message, recipients, purposes) -> None:
        for recipient in recipients:
            distribution = CommunicationMessageRecipient(
                message=message,
                user=recipient,
                channel=CommunicationMessageRecipient.Channel.INTERNAL,
                purpose=cls._purpose_for(str(recipient.pk), purposes),
            )
            distribution.full_clean()
            distribution.save()

    @classmethod
    def _create_external_distributions(cls, message, recipients, purposes) -> None:
        for recipient in recipients:
            distribution = CommunicationMessageRecipient(
                message=message,
                external_participant=recipient,
                destination_email=recipient.email,
                channel=CommunicationMessageRecipient.Channel.EMAIL,
                purpose=cls._purpose_for(str(recipient.pk), purposes),
            )
            distribution.full_clean()
            distribution.save()

    @classmethod
    def _create_direct_email_distributions(cls, message, recipients, purposes) -> None:
        for recipient in recipients:
            distribution = CommunicationMessageRecipient(
                message=message,
                destination_email=recipient,
                channel=CommunicationMessageRecipient.Channel.EMAIL,
                purpose=cls._purpose_for(recipient, purposes),
            )
            distribution.full_clean()
            distribution.save()

    @staticmethod
    def _purpose_for(recipient_id: str, purposes: Mapping[str, str] | None) -> str:
        value = (purposes or {}).get(recipient_id, CommunicationMessageRecipient.Purpose.INFORMATION)
        if value not in CommunicationMessageRecipient.Purpose.values:
            raise ValidationError({"purpose": "Le type de diffusion est invalide."})
        return value

    @staticmethod
    def _unique_users(recipients: Iterable[User]) -> list[User]:
        return list({recipient.pk: recipient for recipient in recipients}.values())

    @staticmethod
    def _unique_external_participants(recipients: Iterable[ProjectExternalParticipant]) -> list[ProjectExternalParticipant]:
        return list({recipient.pk: recipient for recipient in recipients}.values())

    @staticmethod
    def _unique_email_addresses(recipients: Iterable[str]) -> list[str]:
        result = []
        seen = set()
        for value in recipients:
            email = (value or "").strip().lower()
            if not email:
                continue
            validate_email(email)
            if email not in seen:
                seen.add(email)
                result.append(email)
        return result
    
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
        recipient_purposes: Mapping[str, str] | None = None,
    ) -> CommunicationMessage:
        return cls.send_project_message(
            conversation=conversation,
            author=author,
            subject=subject,
            body=body,
            internal_recipients=recipients,
            recipient_purposes=recipient_purposes,
        )

    @classmethod
    @transaction.atomic
    def send_email_message(
        cls,
        *,
        conversation: CommunicationConversation,
        author: User,
        body: str,
        recipients: Iterable[ProjectExternalParticipant],
        subject: str = "",
        recipient_purposes: Mapping[str, str] | None = None,
    ) -> CommunicationMessage:
        return cls.send_project_message(
            conversation=conversation,
            author=author,
            subject=subject,
            body=body,
            external_recipients=recipients,
            recipient_purposes=recipient_purposes,
        )    
