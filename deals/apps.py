from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete


def create_deal_analytics_event(sender, instance, created, **kwargs):
    from .models import DealAnalyticsEvent
    if created:
        # Nur Analytics-Events erstellen, wenn User Opt-In gegeben hat
        user = getattr(instance, 'created_by', None)
        if user and user.analytics_opt_in:
            DealAnalyticsEvent.objects.create(
                event_type='created',
                deal=instance,
                user=user
            )

class DealsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deals'

    def ready(self):
        from .models import Deal
        post_save.connect(create_deal_analytics_event, sender=Deal)
