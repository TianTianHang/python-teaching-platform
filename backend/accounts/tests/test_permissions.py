"""
Tests for accounts app permissions.
"""
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from unittest.mock import Mock

from accounts.permissions import IsSubscriptionActive
from accounts.tests.factories import UserFactory, MembershipTypeFactory, SubscriptionFactory


class IsSubscriptionActivePermissionTest(TestCase):
    """Tests for the IsSubscriptionActive permission."""

    def setUp(self):
        """Set up test fixtures."""
        self.permission = IsSubscriptionActive()
        self.view = Mock()

    def test_returns_false_for_unauthenticated_users(self):
        """Test that permission returns False for unauthenticated users."""
        request = Mock()
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_returns_false_for_users_without_subscription(self):
        """Test that permission returns False for users without subscription."""
        user = UserFactory()
        request = Mock()
        request.user = user
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_returns_false_for_users_with_expired_subscription(self):
        """Test that permission returns False for users with expired subscription."""
        user = UserFactory()
        membership_type = MembershipTypeFactory(duration_days=30)
        SubscriptionFactory(
            user=user,
            membership_type=membership_type,
            expired=True
        )
        request = Mock()
        request.user = user
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_returns_true_for_users_with_active_subscription(self):
        """Test that permission returns True for users with active subscription."""
        user = UserFactory()
        membership_type = MembershipTypeFactory(duration_days=30)
        SubscriptionFactory(
            user=user,
            membership_type=membership_type
        )
        request = Mock()
        request.user = user
        self.assertTrue(self.permission.has_permission(request, self.view))

    def test_returns_false_for_users_with_inactive_subscription(self):
        """Test that permission returns False for users with inactive subscription."""
        user = UserFactory()
        membership_type = MembershipTypeFactory(duration_days=30)
        SubscriptionFactory(
            user=user,
            membership_type=membership_type,
            is_active=False
        )
        request = Mock()
        request.user = user
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_returns_true_for_users_with_multiple_subscriptions_one_active(self):
        """Test that permission returns True if at least one subscription is active."""
        user = UserFactory()
        membership_type1 = MembershipTypeFactory(duration_days=30)
        membership_type2 = MembershipTypeFactory(duration_days=60)
        # Create expired subscription
        SubscriptionFactory(
            user=user,
            membership_type=membership_type1,
            expired=True
        )
        # Create active subscription
        SubscriptionFactory(
            user=user,
            membership_type=membership_type2
        )
        request = Mock()
        request.user = user
        self.assertTrue(self.permission.has_permission(request, self.view))
