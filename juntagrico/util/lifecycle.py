def handle_activated_deactivated(instance, sender, activated, deactivated):
    # if deactivation_date is not none the instance has already been activated once an reactivation or redeactivation is not possible
    if instance.deactivation_date is None:
        if instance._old['active'] != instance.active and instance._old['active'] is False:
            activated.send(sender=sender, instance=instance)
        elif instance._old['active'] != instance.active and instance._old['active'] is True:
            deactivated.send(sender=sender, instance=instance)
