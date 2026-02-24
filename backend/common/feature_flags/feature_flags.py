"""
Feature flag implementation for gradual rollout of new cache features.

This module provides a feature flag system that allows:
1. Gradual rollout of new features
2. A/B testing capabilities
3. Quick rollback in case of issues
4. User-based feature targeting
"""

import logging
from typing import Dict, Any, Optional, List
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings
from enum import Enum

logger = logging.getLogger(__name__)
User = get_user_model()


class Feature(Enum):
    """Available features for rollout"""
    ENHANCED_CACHE = "enhanced_cache"  # New cache with penetration protection
    CACHE_WARMING = "cache_warming"   # Cache warming system
    CACHE_MONITORING = "cache_monitoring"  # Prometheus metrics
    RATE_LIMITING = "rate_limiting"    # DRF rate limiting


class RolloutStrategy(Enum):
    """Rollout strategy for features"""
    OFF = "off"                      # Feature is disabled for everyone
    GRADUAL = "gradual"             # Gradual rollout by percentage
    WHITELIST = "whitelist"         # Only specific users/groups
    ON = "on"                       # Feature is enabled for everyone
    BETA = "beta"                   # Beta testers only


class FeatureFlagService:
    """
    Service to manage feature flags and rollout strategies.
    """

    # Default rollout strategies
    DEFAULT_STRATEGIES = {
        Feature.ENHANCED_CACHE: RolloutStrategy.GRADUAL,
        Feature.CACHE_WARMING: RolloutStrategy.GRADUAL,
        Feature.CACHE_MONITORING: RolloutStrategy.ON,
        Feature.RATE_LIMITING: RolloutStrategy.ON,
    }

    # Default percentages for gradual rollout
    DEFAULT_PERCENTAGES = {
        Feature.ENHANCED_CACHE: 0,  # Start at 0, gradually increase
        Feature.CACHE_WARMING: 0,
        Feature.CACHE_MONITORING: 100,
        Feature.RATE_LIMITING: 100,
    }

    # Whitelists for specific features
    DEFAULT_WHITELISTS = {
        Feature.ENHANCED_CACHE: [],
        Feature.CACHE_WARMING: [],
        Feature.CACHE_MONITORING: [],
        Feature.RATE_LIMITING: [],
    }

    @classmethod
    def get_cache_key(cls, feature: Feature) -> str:
        """Get cache key for feature flag"""
        return f"feature_flag:{feature.value}"

    @classmethod
    def is_enabled(cls, feature: Feature, user: Optional[User] = None) -> bool:
        """
        Check if a feature is enabled for a specific user.

        Args:
            feature: The feature to check
            user: Optional user for personalized rollout

        Returns:
            bool: True if feature is enabled for this user
        """
        try:
            # Get rollout strategy from cache or database
            strategy = cls._get_strategy(feature)
            percentage = cls._get_percentage(feature)
            whitelist = cls._get_whitelist(feature)

            if strategy == RolloutStrategy.OFF:
                return False
            elif strategy == RolloutStrategy.ON:
                return True
            elif strategy == RolloutStrategy.BETA:
                # Only staff/superusers get beta features
                return user and user.is_staff
            elif strategy == RolloutStrategy.WHITELIST:
                return user and user.id in whitelist
            elif strategy == RolloutStrategy.GRADUAL:
                if not user:
                    return False
                # Use user ID hash for consistent distribution
                return cls._is_user_in_percentage(user, percentage)

            return False

        except Exception as e:
            logger.error(f"Error checking feature flag {feature}: {e}")
            return False

    @classmethod
    def _get_strategy(cls, feature: Feature) -> RolloutStrategy:
        """Get rollout strategy for a feature"""
        # Try cache first
        cache_key = f"{cls.get_cache_key(feature)}_strategy"
        cached = cache.get(cache_key)
        if cached is not None:
            return RolloutStrategy(cached)

        # Get from settings or use default
        strategy_name = getattr(settings, f"FEATURE_FLAG_{feature.value.upper()}_STRATEGY", None)

        if strategy_name:
            strategy = RolloutStrategy(strategy_name)
        else:
            strategy = cls.DEFAULT_STRATEGIES[feature]

        # Cache for 5 minutes
        cache.set(cache_key, strategy.value, 300)
        return strategy

    @classmethod
    def _get_percentage(cls, feature: Feature) -> int:
        """Get rollout percentage for gradual rollout"""
        cache_key = f"{cls.get_cache_key(feature)}_percentage"
        cached = cache.get(cache_key)
        if cached is not None:
            return int(cached)

        # Get from settings or use default
        percentage = getattr(settings, f"FEATURE_FLAG_{feature.value.upper()}_PERCENTAGE", cls.DEFAULT_PERCENTAGES[feature])

        # Cache for 5 minutes
        cache.set(cache_key, percentage, 300)
        return percentage

    @classmethod
    def _get_whitelist(cls, feature: Feature) -> List[int]:
        """Get whitelist for a feature"""
        cache_key = f"{cls.get_cache_key(feature)}_whitelist"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Get from settings or use default
        whitelist = getattr(settings, f"FEATURE_FLAG_{feature.value.upper()}_WHITELIST", cls.DEFAULT_WHITELISTS[feature])

        # Cache for 5 minutes
        cache.set(cache_key, whitelist, 300)
        return whitelist

    @classmethod
    def _is_user_in_percentage(cls, user: User, percentage: int) -> bool:
        """
        Determine if a user is in the rollout percentage.

        Uses a hash of user ID for consistent distribution across requests.
        """
        if percentage >= 100:
            return True
        if percentage <= 0:
            return False

        # Use hash of user ID for consistent distribution
        # This ensures the same user always gets the same feature
        user_hash = hash(str(user.id)) % 100
        return user_hash < percentage

    @classmethod
    def enable_feature(cls, feature: Feature):
        """Enable a feature for everyone"""
        cache_key = f"{cls.get_cache_key(feature)}_strategy"
        cache.set(cache_key, RolloutStrategy.ON.value, 300)

        # Log the change
        logger.info(f"Feature {feature.value} enabled for all users")

    @classmethod
    def disable_feature(cls, feature: Feature):
        """Disable a feature for everyone"""
        cache_key = f"{cls.get_cache_key(feature)}_strategy"
        cache.set(cache_key, RolloutStrategy.OFF.value, 300)

        # Log the change
        logger.info(f"Feature {feature.value} disabled for all users")

    @classmethod
    def set_percentage(cls, feature: Feature, percentage: int):
        """Set rollout percentage for gradual rollout"""
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")

        cache_key = f"{cls.get_cache_key(feature)}_percentage"
        cache.set(cache_key, percentage, 300)

        # Log the change
        logger.info(f"Feature {feature.value} rollout percentage set to {percentage}%")

    @classmethod
    def add_to_whitelist(cls, feature: Feature, user_id: int):
        """Add a user to the whitelist"""
        cache_key = f"{cls.get_cache_key(feature)}_whitelist"
        whitelist = cls._get_whitelist(feature)

        if user_id not in whitelist:
            whitelist.append(user_id)
            cache.set(cache_key, whitelist, 300)

            # Log the change
            logger.info(f"User {user_id} added to {feature.value} whitelist")

    @classmethod
    def remove_from_whitelist(cls, feature: Feature, user_id: int):
        """Remove a user from the whitelist"""
        cache_key = f"{cls.get_cache_key(feature)}_whitelist"
        whitelist = cls._get_whitelist(feature)

        if user_id in whitelist:
            whitelist.remove(user_id)
            cache.set(cache_key, whitelist, 300)

            # Log the change
            logger.info(f"User {user_id} removed from {feature.value} whitelist")

    @classmethod
    def get_feature_status(cls, feature: Feature) -> Dict[str, Any]:
        """Get current status of a feature"""
        return {
            'feature': feature.value,
            'strategy': cls._get_strategy(feature).value,
            'percentage': cls._get_percentage(feature),
            'whitelist_count': len(cls._get_whitelist(feature)),
            'enabled': cls.is_enabled(feature),
        }

    @classmethod
    def get_all_features_status(cls) -> Dict[str, Any]:
        """Get status of all features"""
        return {
            feature.value: cls.get_feature_status(feature)
            for feature in Feature
        }


# Convenience functions
def is_cache_feature_enabled(user: Optional[User] = None) -> bool:
    """Check if enhanced cache feature is enabled"""
    return FeatureFlagService.is_enabled(Feature.ENHANCED_CACHE, user)


def is_warming_feature_enabled(user: Optional[User] = None) -> bool:
    """Check if cache warming feature is enabled"""
    return FeatureFlagService.is_enabled(Feature.CACHE_WARMING, user)


def is_monitoring_feature_enabled(user: Optional[User] = None) -> bool:
    """Check if cache monitoring feature is enabled"""
    return FeatureFlagService.is_enabled(Feature.CACHE_MONITORING, user)


def is_rate_limiting_feature_enabled(user: Optional[User] = None) -> bool:
    """Check if rate limiting feature is enabled"""
    return FeatureFlagService.is_enabled(Feature.RATE_LIMITING, user)


def enable_cache_feature():
    """Enable enhanced cache feature for everyone"""
    FeatureFlagService.enable_feature(Feature.ENHANCED_CACHE)


def disable_cache_feature():
    """Disable enhanced cache feature for everyone"""
    FeatureFlagService.disable_feature(Feature.ENHANCED_CACHE)