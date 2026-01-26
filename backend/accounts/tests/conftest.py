"""
Shared fixtures and utilities for accounts app tests.

This module provides common test setup and helper functions
that can be used across multiple test modules.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.tests.factories import (
    UserFactory,
    MembershipTypeFactory,
    SubscriptionFactory,
)


class AccountsTestCase(TestCase):
    """
    Base test case class for accounts app tests.

    Provides common setup and utility methods for testing
    accounts functionality.
    """

    def setUp(self):
        """Set up common test fixtures."""
        self.client = APIClient()

    def create_authenticated_client(self, user=None):
        """
        Create an authenticated API client.

        Args:
            user: Optional User instance. If None, creates a new user.

        Returns:
            Tuple of (APIClient, User) with the client authenticated as the user.
        """
        if user is None:
            user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        return client, user

    def create_admin_client(self):
        """
        Create an authenticated API client for an admin user.

        Returns:
            Tuple of (APIClient, User) with the client authenticated as an admin.
        """
        admin = UserFactory(admin=True)
        client = APIClient()
        client.force_authenticate(user=admin)
        return client, admin

    def create_user_with_subscription(self, user=None, **kwargs):
        """
        Create a user with an active subscription.

        Args:
            user: Optional User instance. If None, creates a new user.
            **kwargs: Additional arguments for SubscriptionFactory.

        Returns:
            Tuple of (User, Subscription).
        """
        if user is None:
            user = UserFactory()
        membership_type = kwargs.pop('membership_type', None)
        if membership_type is None:
            membership_type = MembershipTypeFactory()
        subscription = SubscriptionFactory(
            user=user,
            membership_type=membership_type,
            **kwargs
        )
        return user, subscription


def get_test_password():
    """
    Get a valid test password that meets validation requirements.

    Returns:
        A password string that satisfies Django's password validators.
    """
    return 'TestPass123!'


def create_test_user_data(**overrides):
    """
    Create test user data for registration or update.

    Args:
        **overrides: Optional field overrides.

    Returns:
        Dictionary with user data suitable for API requests.
    """
    data = {
        'username': 'testuser',
        'password': get_test_password(),
        'st_number': '2024999999',
        'email': 'test@example.com',
    }
    data.update(overrides)
    return data
