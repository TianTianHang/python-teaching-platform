"""
Tests for accounts app membership views.
"""
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.tests.factories import MembershipTypeFactory


class MembershipTypeListViewTest(TransactionTestCase):
    """Tests for the MembershipTypeListView."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        # Create active membership types with various durations
        self.membership_1 = MembershipTypeFactory(
            name='Basic',
            duration_days=7,
            price='9.99',
            is_active=True
        )
        self.membership_2 = MembershipTypeFactory(
            name='Premium',
            duration_days=30,
            price='29.99',
            is_active=True
        )
        self.membership_3 = MembershipTypeFactory(
            name='Enterprise',
            duration_days=365,
            price='99.99',
            is_active=True
        )
        # Create inactive membership type
        self.inactive_membership = MembershipTypeFactory(
            name='Old Plan',
            duration_days=15,
            price='19.99',
            is_active=False
        )

    def test_returns_only_active_membership_types(self):
        """Test that only active membership types are returned."""
        url = reverse('membership-type-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response is wrapped in 'results' key
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            self.assertGreaterEqual(len(results), 3)
        else:
            # Response is directly a list
            self.assertGreaterEqual(len(response.data), 3)

    def test_ordered_by_duration_days(self):
        """Test that results are ordered by duration_days."""
        url = reverse('membership-type-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response is wrapped in 'results' key
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            durations = [item['duration_days'] for item in results]
            self.assertEqual(durations, sorted(durations))
        else:
            # Response is directly a list
            durations = [item['duration_days'] for item in response.data]
            self.assertEqual(durations, sorted(durations))

    def test_no_authentication_required(self):
        """Test that no authentication is required."""
        url = reverse('membership-type-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_includes_all_fields(self):
        """Test that response includes all expected fields."""
        url = reverse('membership-type-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response is wrapped in 'results' key
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            self.assertTrue(len(results) > 0)
            item = results[0]
        else:
            # Response is directly a list
            self.assertTrue(len(response.data) > 0)
            item = response.data[0]
        self.assertIn('id', item)
        self.assertIn('name', item)
        self.assertIn('description', item)
        self.assertIn('price', item)
        self.assertIn('duration_days', item)

    def test_inactive_membership_type_not_in_response(self):
        """Test that inactive membership type is not in response."""
        url = reverse('membership-type-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response is wrapped in 'results' key
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            membership_ids = [item['id'] for item in results]
        else:
            # Response is directly a list
            membership_ids = [item['id'] for item in response.data]
        self.assertNotIn(self.inactive_membership.id, membership_ids)
