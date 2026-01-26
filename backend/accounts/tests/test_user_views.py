"""
Tests for accounts app user views.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tests.factories import UserFactory, MembershipTypeFactory, SubscriptionFactory


class MeViewTest(TestCase):
    """Tests for the MeView."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory(
            username='testuser',
            email='test@example.com',
            st_number='2024000001'
        )

    def test_authenticated_user_can_retrieve_own_profile(self):
        """Test that authenticated user can retrieve own profile."""
        self.client.force_authenticate(user=self.user)
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['st_number'], '2024000001')

    def test_response_includes_subscription_info_if_active(self):
        """Test that response includes subscription info if active."""
        membership_type = MembershipTypeFactory(duration_days=30, name='Premium')
        SubscriptionFactory(user=self.user, membership_type=membership_type)
        self.client.force_authenticate(user=self.user)
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_active_subscription'])
        self.assertIsNotNone(response.data['current_subscription'])

    def test_unauthenticated_request_returns_401(self):
        """Test that unauthenticated request returns 401."""
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserUpdateViewTest(TestCase):
    """Tests for the UserUpdateView."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory(
            username='testuser',
            email='test@example.com'
        )

    def test_user_can_update_own_profile(self):
        """Test that user can update own profile (email, username, avatar)."""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-update')
        data = {
            'email': 'newemail@example.com',
            'username': 'newusername',
            'avatar': 'https://example.com/avatar.jpg'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.avatar, 'https://example.com/avatar.jpg')

    def test_cannot_update_st_number(self):
        """Test that st_number cannot be updated (read-only)."""
        original_st_number = self.user.st_number
        self.client.force_authenticate(user=self.user)
        url = reverse('user-update')
        data = {'st_number': '2999999999'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.st_number, original_st_number)

    def test_unauthenticated_request_returns_401(self):
        """Test that unauthenticated request returns 401."""
        url = reverse('user-update')
        response = self.client.patch(url, {'email': 'new@example.com'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListViewTest(TestCase):
    """Tests for the UserListView."""

    def setUp(self):
        """Set up test client and users."""
        self.client = APIClient()
        self.admin = UserFactory(admin=True)
        self.regular_user = UserFactory()
        # Create additional users for testing pagination
        UserFactory.create_batch(10)

    def test_admin_can_list_all_users(self):
        """Test that admin can list all users."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        if isinstance(response.data, dict):
            results = response.data['results']
            self.assertGreater(len(results), 0)  # Should have at least 1 user
            self.assertIn('count', response.data)
        else:
            # Handle direct list response
            self.assertGreater(len(response.data), 0)

    def test_non_admin_request_returns_403(self):
        """Test that non-admin request returns 403."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_request_returns_401(self):
        """Test that unauthenticated request returns 401."""
        url = reverse('list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_includes_user_count(self):
        """Test that response includes user count."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated response
        self.assertIsInstance(response.data, dict)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)


class UserDeleteViewTest(TestCase):
    """Tests for the UserDeleteView."""

    def setUp(self):
        """Set up test client and users."""
        self.client = APIClient()
        self.admin = UserFactory(admin=True)
        self.regular_user = UserFactory()
        self.user_to_delete = UserFactory(username='delete_me')

    def test_admin_can_delete_user(self):
        """Test that admin can delete user."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-delete', kwargs={'pk': self.user_to_delete.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user_to_delete.pk).exists())

    def test_non_admin_request_returns_403(self):
        """Test that non-admin request returns 403."""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('user-delete', kwargs={'pk': self.user_to_delete.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_request_returns_401(self):
        """Test that unauthenticated request returns 401."""
        url = reverse('user-delete', kwargs={'pk': self.user_to_delete.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_user_returns_404(self):
        """Test that deleting non-existent user returns 404."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-delete', kwargs={'pk': 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
