from django.db import migrations, models


def copy_legacy_project_to_projects(apps, schema_editor):
    Conversation = apps.get_model("communications", "CommunicationConversation")
    for conversation in Conversation.objects.exclude(project_id=None).iterator():
        conversation.projects.add(conversation.project_id)


class Migration(migrations.Migration):
    dependencies = [
        ("communications", "0002_communicationmessage_subject_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="communicationconversation",
            name="projects",
            field=models.ManyToManyField(
                blank=True,
                related_name="communication_conversations",
                to="projects.project",
                verbose_name="Projets liés",
            ),
        ),
        migrations.RunPython(
            copy_legacy_project_to_projects,
            migrations.RunPython.noop,
        ),
        migrations.RemoveField(
            model_name="communicationconversation",
            name="project",
        ),
        migrations.AlterModelOptions(
            name="communicationconversation",
            options={
                "ordering": ["-updated_at", "-created_at"],
                "verbose_name": "Conversation",
                "verbose_name_plural": "Conversations",
            },
        ),
    ]
