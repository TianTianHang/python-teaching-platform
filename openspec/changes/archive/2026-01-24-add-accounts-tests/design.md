# Design: accounts App Test Suite

## Architecture Overview

This test suite follows Django's standard testing patterns while introducing factory_boy for test data management. The design prioritizes:

1. **Test Isolation** - Each test is independent with fresh data
2. **Readability** - Clear test names and descriptive assertions
3. **Maintainability** - Factories make test data easy to modify
4. **Coverage** - Unit and integration tests for all critical paths

## Directory Structure

```
backend/accounts/tests/
├── __init__.py                 # Test package marker
├── conftest.py                 # Shared pytest fixtures (if using pytest)
├── factories.py                # Factory Boy definitions
├── test_models.py              # Model logic tests
├── test_serializers.py         # Serializer validation tests
├── test_permissions.py         # Permission class tests
├── test_auth_views.py          # Auth endpoint tests (login, register, logout)
├── test_user_views.py          # User management endpoint tests
├── test_membership_views.py    # Membership endpoint tests
└── test_password_views.py      # Password change endpoint tests
```

## Factory Design

### UserFactory

```python
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    st_number = factory.Sequence(lambda n: f"2024{n:06d}")
    avatar = factory.Faker('paragraph', nb_sentences=1)  # Base64 or URL string

    class Params:
        admin = factory.Trait(
            is_staff=True,
            is_superuser=True,
        )
        with_st_number = factory.Trait(
            st_number=factory.Sequence(lambda n: f"2024{n:06d}"),
        )
```

### MembershipTypeFactory

```python
class MembershipTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MembershipType

    name = factory.Faker('word')
    description = factory.Faker('paragraph')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    duration_days = factory.Faker('random_int', min=7, max=365)
    is_active = True

    class Params:
        inactive = factory.Trait(
            is_active=False,
        )
```

### SubscriptionFactory

```python
class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    membership_type = factory.SubFactory(MembershipTypeFactory)
    start_date = factory.LazyFunction(timezone.now)
    end_date = None  # Auto-calculated
    is_active = True

    class Params:
        expired = factory.Trait(
            start_date=factory.LazyAttribute(
                lambda o: timezone.now() - timezone.timedelta(days=o.membership_type.duration_days + 10)
            ),
        )
```

## Test Patterns

### 1. API Endpoint Tests

Standard pattern for testing views:

```python
class LoginViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory(password='testpass123')
        self.client = APIClient()

    def test_login_with_username_returns_tokens(self):
        url = reverse('login')
        response = self.client.post(url, {
            'username': self.user.username,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
```

### 2. Serializer Validation Tests

Pattern for testing serializer validation:

```python
class RegisterUserSerializerTests(TestCase):
    def test_duplicate_st_number_raises_error(self):
        UserFactory(st_number='2024000001')
        serializer = RegisterUserSerializer(data={
            'username': 'newuser',
            'password': 'TestPass123!',
            'st_number': '2024000001'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('st_number', serializer.errors)
```

### 3. Permission Tests

Pattern for testing permission classes:

```python
class IsSubscriptionActiveTests(TestCase):
    def test_unauthenticated_user_denied(self):
        request = MockRequest(user=AnonymousUser())
        permission = IsSubscriptionActive()
        self.assertFalse(permission.has_permission(request, None))
```

## Configuration Requirements

### pyproject.toml Addition

```toml
dependencies = [
    # ... existing dependencies
    "factory-boy>=3.3.0",
]
```

### Test Settings (if needed)

If custom test settings are required, they can be added to `backend/config/settings/test.py`:

```python
from .base import *

# Test-specific settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Speed up password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
```

## Test Execution

```bash
# Run all accounts tests
uv run python manage.py test accounts.tests

# Run specific test module
uv run python manage.py test accounts.tests.test_auth_views

# Run with verbosity
uv run python manage.py test accounts.tests --verbosity=2

# Run specific test case
uv run python manage.py test accounts.tests.test_auth_views.LoginViewTests
```

## Coverage Goals

| Component | Target Coverage |
|-----------|-----------------|
| Models | 90%+ |
| Serializers | 90%+ |
| Permissions | 100% |
| Views | 85%+ |
| Overall | 85%+ |

## Trade-offs

### factory_boy vs Model Mommy
**Chosen**: factory_boy
- More mature, larger community
- Better Faker integration
- More flexible trait system
- Clearer documentation

### Separate Files vs Single File
**Chosen**: Separate files by feature
- Easier navigation for large test suites
- Clearer organization of related tests
- Better git diff visualization
- Slightly more boilerplate

### TestCase vs APITestCase
**Chosen**: APITestCase for view tests, TestCase for model/serializer tests
- APITestCase provides authenticated client helpers
- TestCase is faster for non-API tests
- Clear separation of concerns

## Future Considerations

1. **pytest migration**: Consider migrating to pytest for better fixtures and parametrized tests
2. **Coverage reporting**: Integrate coverage.py into CI/CD pipeline
3. **Load testing**: Add Locust tests for authentication endpoints
4. **Integration tests**: Consider adding full-stack tests that include frontend authentication flow
