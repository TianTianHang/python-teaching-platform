"""
Tests for accounts app password views.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.tests.factories import UserFactory


class ChangePasswordViewTest(TestCase):
    """Tests for the ChangePasswordView."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory()
        self.user.set_password('oldpass123')
        self.user.save()
        self.url = reverse('change-password')

    def test_successful_password_change_returns_200(self):
        """Test that successful password change returns 200."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpass123',
            'new_password': 'NewPass123!'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_old_password_incorrect_returns_400(self):
        """Test that incorrect old password returns 400."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpass',
            'new_password': 'NewPass123!'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_password_validation_enforced(self):
        """Test that new password validation is enforced."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpass123',
            'new_password': '123'  # Too short
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_login_with_new_password_after_change(self):
        """Test that user can login with new password after change."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpass123',
            'new_password': 'NewPass123!'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to login with new password
        self.client.force_authenticate(user=None)
        login_response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'NewPass123!'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_cannot_login_with_old_password_after_change(self):
        """Test that user cannot login with old password after change."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpass123',
            'new_password': 'NewPass123!'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to login with old password
        self.client.force_authenticate(user=None)
        login_response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'oldpass123'
        })
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_request_returns_401(self):
        """Test that unauthenticated request returns 401."""
        data = {
            'old_password': 'oldpass123',
            'new_password': 'NewPass123!'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_old_password_returns_400(self):
        """Test that missing old password returns 400."""
        self.client.force_authenticate(user=self.user)
        data = {
            'new_password': 'NewPass123!'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_new_password_returns_400(self):
        """Test that missing new password returns 400."""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'oldpass123'
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
