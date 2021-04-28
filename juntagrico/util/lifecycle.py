def handle_activated_deactivated(instance, sender, activated, deactivated):
    # if old deactivation_date is not none the instance has already been activated once an reactivation or redeactivation is not possible
    if instance._old['deactivation_date'] is None:
        if instance._old['activation_date'] is None and instance.activation_date is not None:
            activated.send(sender=sender, instance=instance)
        elif instance._old['deactivation_date'] is None and instance.deactivation_date is not None:
            deactivated.send(sender=sender, instance=instance)


def cancel_extra_sub(extra):
    if extra.deactivation_date is not None:
        extra.cancel()
    elif extra.activation_date is None and extra.deactivation_date is None:
        extra.delete()
