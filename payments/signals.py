from django.db.models.signals import post_save
from django.dispatch import receiver
from payments.models import Payment
from borrowings.telegram_actions import send_notification


@receiver(post_save, sender=Payment)
def notify_payment_creation(sender, instance, created, **kwargs):
    if created:
        message = (f"Payment created :\n"
                   f"payment id: {instance.id}\n"
                   f"type: {instance.type}\n"
                   f"status: {instance.status}\n"
                   f"URL: {instance.session_url}\n"
                   f"money to pay: {instance.money_to_pay}")
        send_notification(message)
