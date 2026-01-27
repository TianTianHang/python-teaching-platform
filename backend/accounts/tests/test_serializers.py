"""
Tests for accounts app serializers.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock

from accounts.models import User, MembershipType, Subscription
from accounts.serializers import (
    RegisterUserSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    MembershipTypeSerializer,
    SubscriptionSerializer,
)
from accounts.tests.factories import (
    UserFactory,
    MembershipTypeFactory,
    SubscriptionFactory,
)


class RegisterUserSerializerTest(TestCase):
    """Tests for the RegisterUserSerializer."""

    def test_valid_registration_creates_user_with_hashed_password(self):
        """Test that valid registration creates user with hashed password."""
        data = {
            'username': 'newuser',
            'password': 'TestPass123!',
            'st_number': '2024999999'
        }
        serializer = RegisterUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.st_number, '2024999999')
        self.assertNotEqual(user.password, 'TestPass123!')  # Password should be hashed
        self.assertTrue(user.check_password('TestPass123!'))

    def test_duplicate_st_number_raises_validation_error(self):
        """Test that duplicate st_number raises validation error."""
        UserFactory(st_number='2024000001')
        data = {
            'username': 'newuser',
            'password': 'TestPass123!',
            'st_number': '2024000001'
        }
        serializer = RegisterUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('st_number', serializer.errors)

    def test_password_validation_enforced(self):
        """Test that password validation is enforced."""
        data = {
            'username': 'newuser',
            'password': '123',  # Too short
            'st_number': '2024999999'
        }
        serializer = RegisterUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_missing_required_fields_return_errors(self):
        """Test that missing required fields return errors."""
        serializer = RegisterUserSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        self.assertIn('password', serializer.errors)
        self.assertIn('st_number', serializer.errors)

    def test_missing_st_number_returns_error(self):
        """Test that missing st_number returns error."""
        data = {
            'username': 'newuser',
            'password': 'TestPass123!'
        }
        serializer = RegisterUserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('st_number', serializer.errors)


class CustomTokenObtainPairSerializerTest(TestCase):
    """Tests for the CustomTokenObtainPairSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory(username='testuser', st_number='2024000001')
        self.user.set_password('testpass123')
        self.user.save()

    def test_login_with_username_works(self):
        """Test that login with username works."""
        serializer = CustomTokenObtainPairSerializer(data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertTrue(serializer.is_valid())
        data = serializer.validated_data
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['st_number'], '2024000001')

    def test_login_with_st_number_works(self):
        """Test that login with st_number works."""
        serializer = CustomTokenObtainPairSerializer(data={
            'username': '2024000001',
            'password': 'testpass123'
        })
        self.assertTrue(serializer.is_valid())
        data = serializer.validated_data
        self.assertIn('access', data)
        self.assertIn('refresh', data)

    def test_invalid_credentials_return_appropriate_error(self):
        """Test that invalid credentials return appropriate error."""
        serializer = CustomTokenObtainPairSerializer(data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_inactive_user_cannot_login(self):
        """Test that inactive user cannot login."""
        self.user.is_active = False
        self.user.save()
        serializer = CustomTokenObtainPairSerializer(data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_nonexistent_user_returns_error(self):
        """Test that non-existent user returns error."""
        serializer = CustomTokenObtainPairSerializer(data={
            'username': 'nonexistent',
            'password': 'testpass123'
        })
        self.assertFalse(serializer.is_valid())

    def test_token_contains_custom_claims(self):
        """Test that token contains custom claims (username, st_number)."""
        serializer = CustomTokenObtainPairSerializer(data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertTrue(serializer.is_valid())
        token = serializer.get_token(self.user)
        self.assertEqual(token['username'], 'testuser')
        self.assertEqual(token['st_number'], '2024000001')


class LogoutSerializerTest(TestCase):
    """Tests for the LogoutSerializer."""

    def test_valid_refresh_token_accepted(self):
        """Test that valid refresh token is accepted."""
        serializer = LogoutSerializer(data={'refresh': 'valid_token_string'})
        self.assertTrue(serializer.is_valid())

    def test_missing_refresh_token_rejected(self):
        """Test that missing refresh token is rejected."""
        serializer = LogoutSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('refresh', serializer.errors)


class UserSerializerTest(TestCase):
    """Tests for the UserSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory(
            username='testuser',
            email='test@example.com',
            st_number='2024000001',
            avatar='https://example.com/avatar.jpg'
        )

    def test_read_only_fields_enforced(self):
        """Test that id and st_number are read-only."""
        serializer = UserSerializer()
        self.assertIn('id', serializer.fields)
        self.assertIn('st_number', serializer.fields)
        self.assertTrue(serializer.fields['id'].read_only)
        self.assertTrue(serializer.fields['st_number'].read_only)

    def test_has_active_subscription_returns_false_when_no_subscription(self):
        """Test that has_active_subscription returns False when no subscription."""
        serializer = UserSerializer(self.user)
        self.assertFalse(serializer.data['has_active_subscription'])

    def test_has_active_subscription_returns_true_when_active_subscription(self):
        """Test that has_active_subscription returns True when active subscription."""
        membership_type = MembershipTypeFactory(duration_days=30)
        subscription = SubscriptionFactory(
            user=self.user,
            membership_type=membership_type
        )
        self.user.active_subscription = subscription
        serializer = UserSerializer(self.user)
        self.assertTrue(serializer.data['has_active_subscription'])

    def test_has_active_subscription_returns_false_when_expired_subscription(self):
        """Test that has_active_subscription returns False when expired subscription."""
        membership_type = MembershipTypeFactory(duration_days=30)
        subscription = SubscriptionFactory(
            user=self.user,
            membership_type=membership_type,
            expired=True
        )
        self.user.active_subscription = subscription
        serializer = UserSerializer(self.user)
        self.assertFalse(serializer.data['has_active_subscription'])

    def test_current_subscription_returns_subscription_details_if_active(self):
        """Test that current_subscription returns subscription details if active."""
        membership_type = MembershipTypeFactory(duration_days=30, name='Premium')
        subscription = SubscriptionFactory(
            user=self.user,
            membership_type=membership_type
        )
        self.user.active_subscription = subscription
        serializer = UserSerializer(self.user)
        self.assertIsNotNone(serializer.data['current_subscription'])
        self.assertEqual(serializer.data['current_subscription']['membership_type']['name'], 'Premium')

    def test_current_subscription_returns_none_if_no_subscription(self):
        """Test that current_subscription returns None if no subscription."""
        serializer = UserSerializer(self.user)
        self.assertIsNone(serializer.data['current_subscription'])

    def test_update_allows_email_username_avatar(self):
        """Test that update allows email, username, and avatar."""
        serializer = UserSerializer(
            self.user,
            data={
                'email': 'newemail@example.com',
                'username': 'newusername',
                'avatar': 'https://example.com/newavatar.jpg'
            },
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.email, 'newemail@example.com')
        self.assertEqual(updated_user.username, 'newusername')
        self.assertEqual(updated_user.avatar, 'https://example.com/newavatar.jpg')

    def test_update_does_not_change_st_number(self):
        """Test that update does not change st_number."""
        original_st_number = self.user.st_number
        serializer = UserSerializer(
            self.user,
            data={'st_number': '2999999999'},
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.st_number, original_st_number)


class ChangePasswordSerializerTest(TestCase):
    """Tests for the ChangePasswordSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = UserFactory()
        self.user.set_password('oldpass123')
        self.user.save()
        self.request = Mock()
        self.request.user = self.user

    def test_valid_old_password_required(self):
        """Test that valid old password is required."""
        serializer = ChangePasswordSerializer(
            data={
                'old_password': 'wrongpass',
                'new_password': 'NewPass123!'
            },
            context={'request': self.request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)

    def test_new_password_validated(self):
        """Test that new password is validated."""
        serializer = ChangePasswordSerializer(
            data={
                'old_password': 'oldpass123',
                'new_password': '123'  # Too short
            },
            context={'request': self.request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)

    def test_password_hash_updated_on_save(self):
        """Test that password hash is updated on save."""
        serializer = ChangePasswordSerializer(
            data={
                'old_password': 'oldpass123',
                'new_password': 'NewPass123!'
            },
            context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('oldpass123'))
        self.assertTrue(self.user.check_password('NewPass123!'))

    def test_missing_fields_return_errors(self):
        """Test that missing fields return errors."""
        serializer = ChangePasswordSerializer(
            data={},
            context={'request': self.request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
        self.assertIn('new_password', serializer.errors)


class MembershipTypeSerializerTest(TestCase):
    """Tests for the MembershipTypeSerializer."""

    def test_all_fields_are_read_only(self):
        """Test that all fields are read-only."""
        membership_type = MembershipTypeFactory()
        serializer = MembershipTypeSerializer()
        fields = ['id', 'name', 'description', 'price', 'duration_days']
        for field in fields:
            self.assertIn(field, serializer.fields)
            self.assertTrue(serializer.fields[field].read_only)

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains expected fields."""
        membership_type = MembershipTypeFactory(
            name='Premium',
            description='Premium membership',
            price='99.99',
            duration_days=30
        )
        serializer = MembershipTypeSerializer(membership_type)
        data = serializer.data
        self.assertEqual(data['name'], 'Premium')
        self.assertEqual(data['description'], 'Premium membership')
        self.assertEqual(str(data['price']), '99.99')
        self.assertEqual(data['duration_days'], 30)


class SubscriptionSerializerTest(TestCase):
    """Tests for the SubscriptionSerializer."""

    def test_serializer_includes_membership_type_details(self):
        """Test that serializer includes membership type details."""
        membership_type = MembershipTypeFactory(name='Premium')
        subscription = SubscriptionFactory(membership_type=membership_type)
        serializer = SubscriptionSerializer(subscription)
        self.assertEqual(serializer.data['membership_type']['name'], 'Premium')

    def test_all_fields_are_read_only(self):
        """Test that all fields are read-only."""
        subscription = SubscriptionFactory()
        serializer = SubscriptionSerializer()
        fields = ['id', 'membership_type', 'start_date', 'end_date', 'is_active']
        for field in fields:
            self.assertIn(field, serializer.fields)
            self.assertTrue(serializer.fields[field].read_only)
