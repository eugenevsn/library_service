from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from books.serializers import BookSerializer
from books.tests import sample_book
from borrowings.models import Borrowing


def sample_borrowing():
    borrow_date = timezone.now().date()
    return {
        "borrow_date": str(borrow_date),
        "expected_return_date": str(
            borrow_date + timezone.timedelta(days=2)
        ),
        "actual_return_date": "",
        "book": 1,
        "user": 1
    }


def get_borrowing_list_url():
    return reverse("borrowings:borrowing-list")


def get_borrowing_return_url(pk: int):
    return reverse(
        "borrowings:borrowing-return-borrowing",
        kwargs={"pk": pk}
    )


class BorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com", "password"
        )
        self.client.force_authenticate(self.user)
        book_data = sample_book()
        book_data["inventory"] = 0
        book_data["title"] = "Inventory Is Empty"
        book = BookSerializer(data=book_data)
        book.is_valid()
        book.save()

        book_data["inventory"] = 2
        book_data["title"] = "Inventory Not Empty"
        book = BookSerializer(data=book_data)
        book.is_valid()
        book.save()

    def test_post_borrow_date_greater_than_actual_or_expected(self):
        borrowing = sample_borrowing()
        borrowing["expected_return_date"] = "2024-04-04"
        res = self.client.post(
            get_borrowing_list_url(), data=borrowing
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_post_borrow_with_book_inventory_0(self):
        borrowing = sample_borrowing()
        borrowing["book"] = Book.objects.get(title="Inventory Is Empty").id
        res = self.client.post(
            get_borrowing_list_url(), data=borrowing
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, res.status_code)

    def test_book_inventory_when_borrowing_created(self):
        borrowing = sample_borrowing()
        book = Book.objects.get(
            title="Inventory Not Empty"
        )
        borrowing["book"] = book.id
        res = self.client.post(
            get_borrowing_list_url(), data=borrowing
        )
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        self.assertEqual(1, Book.objects.get(id=book.id).inventory)

    def test_post_borrowing_user(self):
        borrowing = sample_borrowing()
        borrowing["book"] = Book.objects.get(title="Inventory Not Empty").id
        res = self.client.post(
            get_borrowing_list_url(), data=borrowing
        )
        self.assertEqual(status.HTTP_201_CREATED, res.status_code)
        self.assertEqual(
            self.user.id,
            Borrowing.objects.get(id=res.data["id"]).user_id
        )


class BorrowingUnauthorizedViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthorized_request(self):
        res1 = self.client.get(get_borrowing_list_url())
        res2 = self.client.post(get_borrowing_list_url(), data={})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res1.status_code)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res2.status_code)


class BorrowingAuthorizedFilteringViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user1@test.com", "password"
        )
        self.other_user = get_user_model().objects.create_superuser(
            "user2@test.com", "password"
        )
        self.client.force_authenticate(self.user)

        book_data = sample_book()
        book_data["inventory"] = 3
        book_data["title"] = "Test"
        book = BookSerializer(data=book_data)
        book.is_valid()
        book.save()

        borrowings = sample_borrowing()
        borrowings["book"] = Book.objects.get(title="Test")
        borrowings["user"] = self.user
        borrowings["actual_return_date"] = str(
            timezone.now().date() + timezone.timedelta(days=5)
        )
        Borrowing.objects.create(**borrowings)

        borrowings.pop("actual_return_date")
        borrowings["user"] = self.other_user
        Borrowing.objects.create(**borrowings)

    def test_get_borrowings_for_user(self):
        res = self.client.get(get_borrowing_list_url())
        self.assertEqual(1, len(res.data))

    def test_get_borrowings_for_admin(self):
        self.client.force_authenticate(self.other_user)
        res = self.client.get(get_borrowing_list_url())
        self.assertEqual(2, len(res.data))

    def test_get_borrowings_with_is_active_filter(self):
        self.client.force_authenticate(self.other_user)
        res = self.client.get(get_borrowing_list_url() + "?is_active=True")
        self.assertEqual(1, len(res.data))

    def test_get_borrowings_with_user_id_filter_as_user(self):
        res = self.client.get(get_borrowing_list_url() + "?user_id=2")
        self.assertEqual(1, len(res.data))

    def test_get_borrowings_with_user_id_filter_as_admin(self):
        self.client.force_authenticate(self.other_user)
        res = self.client.get(get_borrowing_list_url() + "?user_id=1")
        self.assertEqual(1, len(res.data))
