from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from books.models import Book
from library import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(default=timezone.now)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    @staticmethod
    def validate_dates(borrow_date, return_date, error_to_raise):
        if borrow_date > return_date:
            raise error_to_raise(
                "Borrow date cannot be after expected "
                f"{borrow_date} > {return_date}"
            )

    @staticmethod
    def validate_inventory(book, error_to_raise):
        if not book.inventory > 0:
            raise error_to_raise(
                "Inventory: 0, you can`t borrow this book"
            )

    def clean(self):
        borrow_date = self.borrow_date
        if not borrow_date:
            borrow_date = timezone.now().date()
        dates = (self.expected_return_date, self.actual_return_date)
        for return_date in dates:
            if return_date:
                Borrowing.validate_dates(
                    borrow_date,
                    return_date,
                    ValidationError,
                )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return f"{self.book} : {self.borrow_date}"
