from django.db.models.signals import post_save
from django.dispatch import receiver
from borrowings.models import Borrowing
from borrowings.telegram_actions import send_notification


@receiver(post_save, sender=Borrowing)
def notify_borrowing_creation(sender, instance, created, **kwargs):
    if created:
        message = (f":: New borrowing created ::\n"
                   f"id: {instance.id}\n"
                   f"book: {instance.book.title}\n"
                   f"borrow date: {instance.borrow_date}\n"
                   f"borrow by: {instance.user.email}\n"
                   f"return date: {instance.expected_return_date}\n"
                   f"books left: {instance.book.inventory}")
        send_notification(message)
