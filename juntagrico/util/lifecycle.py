def handle_activated_deactivated(instance, sender, activated, deactivated):
    if instance._old['active'] != instance.active and instance._old['active'] is False and instance.deactivation_date is None:
        activated.send(sender=sender, instance=instance)
    elif instance._old['active'] != instance.active and instance._old['active'] is True and instance.deactivation_date is None:
        deactivated.send(sender=sender, instance=instance)
