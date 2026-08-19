
    
from apps.projects.models import Project


def can_review_activity_reports(user) -> bool:
    """
    Retourne True si l'utilisateur peut accéder
    à la validation des rapports d'activité.
    """

    if not user.is_authenticated:
        return False

    if user.global_role.code in {
        "SYSTEM_ADMIN",
        "CLIENT_ADMIN",
    }:
        return True

    return Project.objects.filter(
        project_manager=user,
    ).exists()