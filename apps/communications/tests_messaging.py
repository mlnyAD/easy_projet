from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.catalogs.models import CatalogType, CatalogValue
from apps.companies.models import Company
from apps.communications.models import (
    CommunicationConversation,
    CommunicationMessageRecipient,
)
from apps.communications.services import CommunicationService
from apps.projects.models import Project
from apps.core.models import ClientEnvironment
from apps.users.models import User


class PersonalMessagingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(name="Société messagerie")
        cls.other_company = Company.objects.create(name="Autre société")
        ClientEnvironment.objects.create(company=cls.company)
        ClientEnvironment.objects.create(company=cls.other_company)
        cls.author = User.objects.create(company=cls.company, email="author@example.com", first_name="Anne", last_name="Auteur")
        cls.recipient = User.objects.create(company=cls.company, email="recipient@example.com", first_name="Paul", last_name="Destinataire")
        cls.foreign_user = User.objects.create(company=cls.other_company, email="foreign@example.com", first_name="Marc", last_name="Externe")
        status_type = CatalogType.objects.create(code="TEST_COMM_PROJECT_STATUS", label="Statut")
        status = CatalogValue.objects.create(catalog_type=status_type, code="OPEN", label="Ouvert", sort_order=1)
        cls.project = Project.objects.create(company=cls.company, reference="COM-001", name="Projet communication", status=status)

    def test_conversation_can_be_created_without_project(self):
        conversation = CommunicationService.create_conversation(author=self.author, title="Sujet transverse")
        self.assertEqual(conversation.projects.count(), 0)

    def test_conversation_can_link_several_projects(self):
        conversation = CommunicationService.create_conversation(author=self.author, title="Sujet projet", projects=[self.project])
        self.assertEqual(list(conversation.projects.values_list("pk", flat=True)), [self.project.pk])

    def test_internal_message_is_not_limited_to_project_members(self):
        conversation = CommunicationService.create_conversation(author=self.author, title="Sujet transverse")
        message = CommunicationService.send_message(conversation=conversation, author=self.author, body="Bonjour", internal_recipients=[self.recipient])
        self.assertTrue(message.recipients.filter(user=self.recipient, channel=CommunicationMessageRecipient.Channel.INTERNAL).exists())

    def test_internal_message_rejects_user_from_another_company(self):
        conversation = CommunicationService.create_conversation(author=self.author, title="Sujet")
        with self.assertRaisesMessage(ValidationError, "même société"):
            CommunicationService.send_message(conversation=conversation, author=self.author, body="Bonjour", internal_recipients=[self.foreign_user])

    def test_mark_read_only_changes_current_user_distribution(self):
        conversation = CommunicationService.create_conversation(author=self.author, title="Sujet")
        message = CommunicationService.send_message(conversation=conversation, author=self.author, body="Bonjour", internal_recipients=[self.recipient])
        distribution = message.recipients.get(user=self.recipient)
        self.client.force_login(self.recipient)
        response = self.client.post(f"/communications/conversations/{conversation.pk}/read/")
        self.assertEqual(response.status_code, 200)
        distribution.refresh_from_db()
        self.assertEqual(distribution.status, CommunicationMessageRecipient.Status.READ)
        self.assertIsNotNone(distribution.read_at)
