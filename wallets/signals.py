from django.conf import settings
from django.db.models.signals import post_save

from .models import Registration

from .tasks import pass_push_apple
from .tasks import pass_push_android


def post_save_signal_pass_push(
        instance: settings.PASS_MODEL,
        created,
        **kwargs
):
    """After saving passes"""

    # Update registered devices

    registrations = Registration.objects.filter(pass_object=instance)
    if registrations.exists():
        for registration in registrations:
            try:
                # android tokens are longer
                if len(registration.device.push_token) > 100:
                    pass_push_android.delay(
                        registration.device.push_token
                    )
                else:
                    # pass_push_apple(pass_)
                    pass_push_apple.delay(
                        registration.device.push_token
                    )
            except Exception as e:
                print(e)


if settings.WALLET_ENABLE_NOTIFICATIONS:
    post_save.connect(
        post_save_signal_pass_push,
        sender=settings.PASS_MODEL
    )
