from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentDetailSerializer
from payments.views import payment_success, payment_cancelled

PAYMENTS_URLS = reverse("payments:payment-list")


class PaymentsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="example@mail.com", password="password"
        )
        self.book = Book.objects.create(
            title="Title", author="Author", cover="Hard", inventory=18, daily_fee=1.15
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date="2022-01-01", expected_return_date="2022-01-27",
            actual_return_date="2022-01-28", book=self.book, user=self.user
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT, borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/pay/test_session_id",
            session_id="test_session_id", money_to_pay=32.2
        )

    def test_unauthenticated_access(self):
        res = self.client.get(PAYMENTS_URLS)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.post(PAYMENTS_URLS)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_list(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(PAYMENTS_URLS)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = PaymentListSerializer(Payment.objects.all(), many=True)
        self.assertEqual(res.data, serializer.data)

    def test_payment_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("payments:payment-detail", kwargs={"pk": self.payment.pk})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = PaymentDetailSerializer(self.payment)
        self.assertEqual(res.data, serializer.data)

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_successful(self, mock_retrieve):
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_retrieve.return_value = mock_session

        self.client.force_authenticate(user=self.user)
        res = payment_success(self.client.get("/payment_success_url"), "test_session_id")
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PAID)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.content.decode(), "Payment Successful!")

    @patch("stripe.checkout.Session.retrieve")
    def test_payment_failed(self, mock_retrieve):
        mock_session = MagicMock()
        mock_session.payment_status = "unpaid"
        mock_retrieve.return_value = mock_session

        self.client.force_authenticate(user=self.user)
        res = payment_success(self.client.get("/payment_success_url"), "test_session_id")
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PENDING)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.content.decode(), "Payment Failed.")

    def test_payment_cancel(self):
        # Test payment cancellation
        res = payment_cancelled(self.client.get("/payment_cancelled_url"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.content.decode(),"Payment was cancelled. Please complete the payment within 24 hours.")
