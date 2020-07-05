from django.utils import timezone


def handle_simple_activated(sender, instance, **kwargs):
    instance.activation_date = instance.activation_date or timezone.now().date()


def handle_simple_deactivated(sender, instance, **kwargs):
    instance.deactivation_date = instance.deactivation_date or timezone.now().date()
