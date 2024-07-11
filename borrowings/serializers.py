from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.db import transaction

from borrowings.models import Borrowing
from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        borrow_date = timezone.now().date()
        if "borrow_date" in data.keys():
            borrow_date = data["borrow_date"]
        dates = (
            data["expected_return_date"],
            data["actual_return_date"]
        )
        for return_date in dates:
            if return_date:
                Borrowing.validate_dates(
                    borrow_date,
                    return_date,
                    ValidationError,
                )
        return data

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date",
                  "actual_return_date", "book", "user")


class BorrowingListSerializer(BorrowingSerializer):
    book_title = serializers.CharField(source="book.title")

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date",
                  "actual_return_date", "book_title", "user")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer()


class BorrowingCreateSerializer(BorrowingSerializer):
    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            Borrowing.validate_inventory(
                validated_data["book"],
                ValidationError
            )
            book.inventory -= 1
            book.save()
            return Borrowing.objects.create(**validated_data)

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date",
                  "actual_return_date", "book")
