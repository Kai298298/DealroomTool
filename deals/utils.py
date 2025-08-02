"""
Hilfsfunktionen für die Deals-App
"""
from django.contrib.auth import get_user_model
from .models import DealChangeLog

User = get_user_model()


def log_deal_change(deal, change_type, user, field_name=None, old_value=None, new_value=None, description=None):
    """
    Protokolliert eine Änderung an einem Dealroom
    
    Args:
        deal: Der Dealroom
        change_type: Art der Änderung (aus DealChangeLog.ChangeType)
        user: Der Benutzer, der die Änderung vorgenommen hat
        field_name: Name des geänderten Feldes (optional)
        old_value: Alter Wert (optional)
        new_value: Neuer Wert (optional)
        description: Benutzerdefinierte Beschreibung (optional)
    """
    DealChangeLog.objects.create(
        deal=deal,
        change_type=change_type,
        changed_by=user,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        description=description
    )


def log_deal_creation(deal, user):
    """Protokolliert die Erstellung eines Dealrooms"""
    log_deal_change(
        deal=deal,
        change_type=DealChangeLog.ChangeType.CREATED,
        user=user,
        description=f"Dealroom '{deal.title}' wurde erstellt"
    )


def log_deal_update(deal, user, field_name=None, old_value=None, new_value=None):
    """Protokolliert die Aktualisierung eines Dealrooms"""
    log_deal_change(
        deal=deal,
        change_type=DealChangeLog.ChangeType.UPDATED,
        user=user,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value
    )


def log_status_change(deal, user, old_status, new_status):
    """Protokolliert eine Status-Änderung"""
    log_deal_change(
        deal=deal,
        change_type=DealChangeLog.ChangeType.STATUS_CHANGED,
        user=user,
        field_name='status',
        old_value=old_status,
        new_value=new_status
    )


def log_file_assignment(deal, user, file_title, role):
    """Protokolliert die Zuordnung einer Datei"""
    log_deal_change(
        deal=deal,
        change_type=DealChangeLog.ChangeType.FILE_ASSIGNED,
        user=user,
        new_value=f"{file_title} ({role})",
        description=f"Datei '{file_title}' als {role} zugeordnet"
    )


def log_file_unassignment(deal, user, file_title, role):
    """Protokolliert die Entfernung einer Datei"""
    log_deal_change(
        deal=deal,
        change_type=DealChangeLog.ChangeType.FILE_UNASSIGNED,
        user=user,
        old_value=f"{file_title} ({role})",
        description=f"Datei '{file_title}' als {role} entfernt"
    )


def log_website_generation(deal, user):
    """Protokolliert die Website-Generierung"""
    log_deal_change(
        deal=deal,
        change_type=DealChangeLog.ChangeType.WEBSITE_GENERATED,
        user=user,
        description="Website wurde generiert"
    )


def log_website_deletion(deal, user):
    """Protokolliert die Website-Löschung"""
    log_deal_change(
        deal=deal,
        change_type=DealChangeLog.ChangeType.WEBSITE_DELETED,
        user=user,
        description="Website wurde gelöscht"
    ) 