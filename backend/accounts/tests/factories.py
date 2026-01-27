"""
Factory Boy definitions for accounts app test data.
"""
import factory
from factory import django, fuzzy
from django.utils import timezone
from faker import Faker

from accounts.models import User, MembershipType, Subscription

fake = Faker()


class UserFactory(django.DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    st_number = factory.Sequence(lambda n: f"2024{n:06d}")
    avatar = factory.Faker('paragraph', nb_sentences=1)
    is_active = True

    class Params:
        # Trait for admin users
        admin = factory.Trait(
            is_staff=True,
            is_superuser=True,
        )
        # Trait for users with a specific student number
        with_st_number = factory.Trait(
            st_number=factory.Sequence(lambda n: f"2024{n:06d}"),
        )
        # Trait for users with avatar
        with_avatar = factory.Trait(
            avatar=factory.Faker('paragraph', nb_sentences=1),
        )


class MembershipTypeFactory(django.DjangoModelFactory):
    """Factory for creating MembershipType instances."""

    class Meta:
        model = MembershipType

    name = factory.Sequence(lambda n: f"Membership_{n}")
    description = factory.Faker('paragraph')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    duration_days = factory.Faker('random_int', min=7, max=365)
    is_active = True

    class Params:
        # Trait for inactive membership types
        inactive = factory.Trait(
            is_active=False,
        )


class SubscriptionFactory(django.DjangoModelFactory):
    """Factory for creating Subscription instances."""

    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    membership_type = factory.SubFactory(MembershipTypeFactory)
    start_date = factory.LazyFunction(timezone.now)
    end_date = None  # Auto-calculated from membership_type.duration_days
    is_active = True

    class Params:
        # Trait for expired subscriptions
        expired = factory.Trait(
            start_date=factory.LazyAttribute(
                lambda o: timezone.now() - timezone.timedelta(days=o.membership_type.duration_days + 10)
            ),
        )
