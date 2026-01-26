"""
Tests for accounts app models.
"""
import logging
from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, MembershipType, Subscription
from accounts.tests.factories import UserFactory, MembershipTypeFactory, SubscriptionFactory


class UserModelTest(TestCase):
    """Tests for the User model."""

    def setUp(self):
        """Set up test environment with clean state."""
        super().setUp()
        # Disable logging during tests for cleaner output
        import logging
        logging.disable(logging.CRITICAL)

    def test_str_representation_includes_st_number_and_username(self):
        """Test that __str__ returns 'st_number-username' format."""
        user = UserFactory(st_number='2024000001', username='testuser')
        self.assertEqual(str(user), '2024000001-testuser')

    def test_st_number_uniqueness_constraint(self):
        """Test that st_number must be unique."""
        UserFactory(st_number='2024000001')
        with self.assertRaises(IntegrityError):
            UserFactory(st_number='2024000001')

    def test_avatar_field_accepts_valid_data(self):
        """Test that avatar field can store and retrieve data."""
        avatar_data = 'https://example.com/avatar.jpg'
        user = UserFactory(avatar=avatar_data)
        self.assertEqual(user.avatar, avatar_data)

    def test_avatar_field_can_be_null(self):
        """Test that avatar field can be null."""
        user = UserFactory(avatar=None)
        self.assertIsNone(user.avatar)

    def test_user_is_active_by_default(self):
        """Test that new users are active by default."""
        user = UserFactory()
        self.assertTrue(user.is_active)

    def test_user_with_avatar_trait(self):
        """Test creating user with avatar trait."""
        user = UserFactory(with_avatar=True)
        self.assertIsNotNone(user.avatar)

    def test_admin_user_has_staff_and_superuser_flags(self):
        """Test that admin users have is_staff and is_superuser set."""
        admin = UserFactory(admin=True)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class MembershipTypeModelTest(TestCase):
    """Tests for the MembershipType model."""

    def test_str_representation_returns_name(self):
        """Test that __str__ returns the membership type name."""
        membership_type = MembershipTypeFactory(name='Premium')
        self.assertEqual(str(membership_type), 'Premium')

    def test_is_active_defaults_to_true(self):
        """Test that new membership types are active by default."""
        membership_type = MembershipTypeFactory()
        self.assertTrue(membership_type.is_active)

    def test_inactive_trait_sets_is_active_to_false(self):
        """Test that inactive trait sets is_active to False."""
        membership_type = MembershipTypeFactory(inactive=True)
        self.assertFalse(membership_type.is_active)

    def test_duration_days_is_positive(self):
        """Test that duration_days is a positive integer."""
        membership_type = MembershipTypeFactory()
        self.assertGreater(membership_type.duration_days, 0)

    def test_price_is_decimal(self):
        """Test that price is stored as decimal."""
        membership_type = MembershipTypeFactory(price='99.99')
        self.assertEqual(str(membership_type.price), '99.99')


class SubscriptionModelTest(TestCase):
    """Tests for the Subscription model."""

    def test_str_representation_includes_user_and_membership_type(self):
        """Test that __str__ returns 'username - membership_type_name' format."""
        user = UserFactory(username='testuser')
        membership_type = MembershipTypeFactory(name='Premium')
        subscription = SubscriptionFactory(user=user, membership_type=membership_type)
        self.assertEqual(str(subscription), 'testuser - Premium')

    def test_end_date_auto_calculated_from_duration_days(self):
        """Test that end_date is auto-calculated from membership_type.duration_days."""
        membership_type = MembershipTypeFactory(duration_days=30)
        subscription = SubscriptionFactory(membership_type=membership_type)
        expected_end_date = subscription.start_date + timedelta(days=30)
        # Allow 1 second difference for test execution time
        self.assertAlmostEqual(
            subscription.end_date.timestamp(),
            expected_end_date.timestamp(),
            delta=1
        )

    def test_is_active_defaults_to_true(self):
        """Test that new subscriptions are active by default."""
        subscription = SubscriptionFactory()
        self.assertTrue(subscription.is_active)

    def test_expired_trait_creates_past_subscription(self):
        """Test that expired trait creates a subscription with past start_date."""
        membership_type = MembershipTypeFactory(duration_days=30)
        subscription = SubscriptionFactory(
            membership_type=membership_type,
            expired=True
        )
        # The subscription should have ended more than a week ago
        self.assertLess(subscription.end_date, timezone.now() - timedelta(days=7))

    def test_subscription_can_be_created_with_custom_end_date(self):
        """Test that subscription can be created with a custom end_date."""
        custom_end_date = timezone.now() + timedelta(days=60)
        subscription = SubscriptionFactory(end_date=custom_end_date)
        self.assertEqual(subscription.end_date, custom_end_date)

    def test_subscription_user_relationship(self):
        """Test that subscription correctly relates to user."""
        user = UserFactory(username='testuser')
        subscription = SubscriptionFactory(user=user)
        self.assertEqual(subscription.user, user)

    def test_subscription_membership_type_relationship(self):
        """Test that subscription correctly relates to membership_type."""
        membership_type = MembershipTypeFactory(name='Gold')
        subscription = SubscriptionFactory(membership_type=membership_type)
        self.assertEqual(subscription.membership_type, membership_type)
