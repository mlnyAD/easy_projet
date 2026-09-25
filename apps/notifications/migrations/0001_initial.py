import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("projects", "0007_project_project_photo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Créé le",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="Modifié le",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Identifiant",
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            (
                                "MEETING_INVITATION",
                                "Invitation à une réunion",
                            ),
                        ],
                        max_length=40,
                        verbose_name="Type",
                    ),
                ),
                (
                    "source_key",
                    models.CharField(
                        max_length=255,
                        verbose_name="Clé fonctionnelle",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        max_length=200,
                        verbose_name="Titre",
                    ),
                ),
                (
                    "body",
                    models.TextField(
                        blank=True,
                        max_length=1000,
                        verbose_name="Détail",
                    ),
                ),
                (
                    "target_url",
                    models.CharField(
                        max_length=500,
                        verbose_name="Lien cible",
                    ),
                ),
                (
                    "read_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Lu le",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="projects.project",
                        verbose_name="Projet",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Destinataire",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification",
                "verbose_name_plural": "Notifications",
                "db_table": "notification",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(
                fields=("user", "source_key"),
                name="uniq_notification_user_source_key",
            ),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(
                fields=["user", "read_at", "-created_at"],
                name="notification_user_read_idx",
            ),
        ),
    ]
