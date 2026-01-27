"""
Tests for password hashing with Argon2.

This test suite verifies that:
1. New user passwords are hashed with Argon2id
2. Existing PBKDF2 hashes remain valid (backward compatibility)
3. Passwords automatically migrate to Argon2id on successful login
4. Password changes use Argon2id hashing
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import (
    Argon2PasswordHasher,
    PBKDF2PasswordHasher,
    check_password,
    make_password,
)
from rest_framework.test import APIClient

from accounts.models import User
from accounts.tests.factories import UserFactory


class Argon2PasswordHashingTest(TestCase):
    """Tests for Argon2 password hashing."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()

    def test_new_user_password_hashed_with_argon2(self):
        """Test that new user passwords are hashed with Argon2id."""
        user = UserFactory(username='newuser', st_number='2024000001')
        password = 'SecurePass123!'
        user.set_password(password)
        user.save()

        # Refresh from database to get the stored hash
        user.refresh_from_db()

        # Verify password hash starts with argon2$argon2id
        self.assertTrue(
            user.password.startswith('argon2$argon2id'),
            f"Expected password to start with 'argon2$argon2id', got: {user.password[:30]}"
        )

        # Verify password can be checked
        self.assertTrue(user.check_password(password))

    def test_password_change_uses_argon2(self):
        """Test that password changes use Argon2id hashing."""
        user = UserFactory(username='changuser', st_number='2024000002')
        user.set_password('OldPass123!')
        user.save()

        # Change password
        user.set_password('NewPass456!')
        user.save()
        user.refresh_from_db()

        # Verify new password is hashed with Argon2
        self.assertTrue(
            user.password.startswith('argon2$argon2id'),
            f"Expected password to start with 'argon2$argon2id', got: {user.password[:30]}"
        )
        self.assertTrue(user.check_password('NewPass456!'))

    def test_pbkdf2_backward_compatibility(self):
        """Test that existing PBKDF2 hashes remain valid."""
        # Create a user with PBKDF2 hash (simulate existing user)
        user = UserFactory(username='olduser', st_number='2024000003')
        pbkdf2_hasher = PBKDF2PasswordHasher()
        user.password = pbkdf2_hasher.encode(password='oldpass123', salt='testsalt')
        user.save()

        # Refresh from database
        user.refresh_from_db()

        # Verify PBKDF2 hash can still be checked
        self.assertTrue(
            user.password.startswith('pbkdf2_sha256$'),
            f"Expected PBKDF2 hash, got: {user.password[:30]}"
        )
        self.assertTrue(user.check_password('oldpass123'))

    def test_automatic_migration_to_argon2_on_login(self):
        """Test that passwords automatically migrate to Argon2id on successful login."""
        # Create a user with PBKDF2 hash (simulate existing user)
        user = UserFactory(username='migrateuser', st_number='2024000004')
        pbkdf2_hasher = PBKDF2PasswordHasher()
        old_password = 'migratepass123'
        user.password = pbkdf2_hasher.encode(password=old_password, salt='migratesalt')
        user.save()

        # Verify initial hash is PBKDF2
        user.refresh_from_db()
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))

        # Login with correct credentials (this should trigger migration)
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'migrateuser',
            'password': old_password
        })

        # Login should succeed
        self.assertEqual(response.status_code, 200, f"Login failed: {response.data}")

        # Refresh and check that password has been migrated to Argon2
        user.refresh_from_db()
        self.assertTrue(
            user.password.startswith('argon2$argon2id'),
            f"Expected password to be migrated to Argon2, got: {user.password[:30]}"
        )

        # Verify password still works after migration
        self.assertTrue(user.check_password(old_password))

    def test_login_after_migration_still_works(self):
        """Test that login continues to work after password migration."""
        # Create a user with PBKDF2 hash
        user = UserFactory(username='migrateuser2', st_number='2024000005')
        pbkdf2_hasher = PBKDF2PasswordHasher()
        password = 'aftermigrate123'
        user.password = pbkdf2_hasher.encode(password=password, salt='aftermigratesalt')
        user.save()

        # First login (should trigger migration)
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'migrateuser2',
            'password': password
        })
        self.assertEqual(response.status_code, 200)

        # Second login (should use Argon2 hash)
        response = self.client.post(url, {
            'username': 'migrateuser2',
            'password': password
        })
        self.assertEqual(response.status_code, 200)

    def test_wrong_password_does_not_migrate_hash(self):
        """Test that wrong password does not trigger migration."""
        # Create a user with PBKDF2 hash
        user = UserFactory(username='wrongpassuser', st_number='2024000006')
        pbkdf2_hasher = PBKDF2PasswordHasher()
        user.password = pbkdf2_hasher.encode(password='correctpass', salt='wrongpasssalt')
        user.save()

        # Store the original password hash
        original_hash = user.password

        # Try to login with wrong password
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'wrongpassuser',
            'password': 'wrongpass'
        })

        # Login should fail
        self.assertIn(response.status_code, [400, 401])

        # Hash should NOT be migrated (should still be PBKDF2)
        user.refresh_from_db()
        self.assertEqual(
            user.password,
            original_hash,
            "Password hash should not change after failed login attempt"
        )

    def test_make_password_uses_argon2(self):
        """Test that make_password helper uses Argon2."""
        password = 'testpass123'
        hashed = make_password(password)

        self.assertTrue(
            hashed.startswith('argon2$argon2id'),
            f"Expected make_password to use Argon2, got: {hashed[:30]}"
        )
        self.assertTrue(check_password(password, hashed))
