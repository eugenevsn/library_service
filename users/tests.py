from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse


def sample_user():
    return {
        "email": "user@mail.com",
        "first_name": "test",
        "last_name": "user",
        "password": "12345"
    }


def get_me_url():
    return reverse("users:manage")


def register_url():
    return reverse("users:create")


class UserUnauthorizedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_access_to_me_endpoint(self):
        res = self.client.get(get_me_url())
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, res.status_code)

    def test_register_user_with_short_password(self):
        user_data = sample_user()
        user_data["password"] = "1234"
        response = self.client.post(register_url(), data=user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_data_with_is_staff_true(self):
        user_data = sample_user()
        user_data["is_staff"] = True
        res = self.client.post(register_url(), data=user_data)
        user_id = res.data["id"]
        user = get_user_model().objects.get(id=user_id)
        self.assertTrue(not user.is_staff)


class UserAuthorizerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "password"
        )
        self.client.force_authenticate(self.user)

    def test_put_data_with_is_staff_true(self):
        user_data = sample_user()
        user_data["is_staff"] = True
        res = self.client.put(get_me_url(), user_data)
        user_id = res.data["id"]
        user = get_user_model().objects.get(id=user_id)
        self.assertTrue(not user.is_staff)
