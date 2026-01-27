"""
Tests for accounts app authentication views.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.tests.factories import UserFactory


class LoginViewTest(TestCase):
    """Tests for the LoginView."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        self.user = UserFactory(username='testuser', st_number='2024000001')
        self.user.set_password('testpass123')
        self.user.save()

    def test_successful_login_returns_access_and_refresh_tokens(self):
        """Test that successful login returns access and refresh tokens."""
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_username_works(self):
        """Test that login with username works."""
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_st_number_works(self):
        """Test that login with st_number works."""
        url = reverse('login')
        response = self.client.post(url, {
            'username': '2024000001',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_failed_login_returns_error(self):
        """Test that failed login returns an error."""
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])

    def test_inactive_user_cannot_login(self):
        """Test that inactive user cannot login."""
        self.user.is_active = False
        self.user.save()
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST])

    def test_login_response_includes_user_info(self):
        """Test that login response includes user information."""
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('st_number', response.data)


class RegisterViewTest(TestCase):
    """Tests for the RegisterView."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_successful_registration_creates_user_and_returns_tokens(self):
        """Test that successful registration creates user and returns tokens."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'TestPass123!',
            'st_number': '2024999999'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_duplicate_st_number_returns_400_error(self):
        """Test that duplicate st_number returns 400 error."""
        UserFactory(st_number='2024000001')
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'TestPass123!',
            'st_number': '2024000001'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_username_returns_400_error(self):
        """Test that duplicate username returns 400 error."""
        UserFactory(username='existinguser')
        url = reverse('register')
        data = {
            'username': 'existinguser',
            'password': 'TestPass123!',
            'st_number': '2024999999'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_password_returns_400_error(self):
        """Test that invalid password returns 400 error."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': '123',  # Too short
            'st_number': '2024999999'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields_returns_400_error(self):
        """Test that missing required fields returns 400 error."""
        url = reverse('register')
        data = {
            'username': 'newuser'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTest(TestCase):
    """Tests for the LogoutView."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory()
        self.user.set_password('testpass123')
        self.user.save()
        # Get refresh token
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'testpass123'
        })
        self.refresh_token = response.data['refresh']

    def test_valid_refresh_token_blacklisted(self):
        """Test that valid refresh token is blacklisted."""
        url = reverse('logout')
        response = self.client.post(url, {'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Try to use the blacklisted token - should fail
        response = self.client.post(reverse('refresh'), {'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_refresh_token_returns_400_error(self):
        """Test that missing refresh token returns 400 error."""
        url = reverse('logout')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_refresh_token_returns_500_error(self):
        """Test that invalid refresh token returns 500 error."""
        url = reverse('logout')
        response = self.client.post(url, {'refresh': 'invalid_token'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewTest(TestCase):
    """Tests for the TokenRefreshView (from DRF SimpleJWT)."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory()
        self.user.set_password('testpass123')
        self.user.save()
        # Get refresh token
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'testpass123'
        })
        self.refresh_token = response.data['refresh']

    def test_valid_refresh_token_returns_new_access_token(self):
        """Test that valid refresh token returns new access token."""
        url = reverse('refresh')
        response = self.client.post(url, {'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_refresh_token_returns_error(self):
        """Test that invalid refresh token returns error."""
        url = reverse('refresh')
        response = self.client.post(url, {'refresh': 'invalid_token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenVerifyViewTest(TestCase):
    """Tests for the TokenVerifyView (from DRF SimpleJWT)."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = UserFactory()
        self.user.set_password('testpass123')
        self.user.save()
        # Get access token
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': 'testpass123'
        })
        self.access_token = response.data['access']

    def test_valid_access_token_passes_verification(self):
        """Test that valid access token passes verification."""
        url = reverse('verify')
        response = self.client.post(url, {'token': self.access_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_access_token_fails_verification(self):
        """Test that invalid access token fails verification."""
        url = reverse('verify')
        response = self.client.post(url, {'token': 'invalid_token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
