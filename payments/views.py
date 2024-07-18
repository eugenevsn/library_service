import stripe
from django.db import transaction
from django.http import HttpResponse
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from library import settings
from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["retrieve"]:
            return PaymentDetailSerializer
        return PaymentListSerializer


@transaction.atomic
def payment_success(request, session_id):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        payment = Payment.objects.get(session_id=session_id)
        payment.status = Payment.StatusChoices.PAID
        payment.save()
        return HttpResponse("Payment Successful!")
    else:
        return HttpResponse("Payment Failed.")


def payment_cancelled(request):
    return HttpResponse(
        "Payment was cancelled. Please complete the payment within 24 hours."
    )
