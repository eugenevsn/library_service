from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    cover = models.CharField(max_length=10, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return self.title
