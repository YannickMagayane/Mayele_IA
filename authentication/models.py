"""
User Profile and Quota Management Models for Authentication.

This module defines user roles (Student, Decision Maker, Doyen Admin) and API quota limit counters
to protect the AI Pro paid account usage.

:Example:

>>> from django.contrib.auth.models import User
>>> from authentication.models import UserProfile
>>> user = User.objects.create(username="test_user")
>>> profile = UserProfile.objects.create(user=user, role="etudiant")
>>> print(profile.get_quota_limit())
50
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    User profile model extending Django User with role-based quotas.

    :param user: One-to-one relationship with standard Django User.
    :type user: django.contrib.auth.models.User
    :param role: User role determining authorization and daily API quotas.
    :type role: str
    :param daily_quota: Max number of daily requests allowed.
    :type daily_quota: int
    :param tokens_used_today: Count of API requests performed today.
    :type tokens_used_today: int
    :param last_quota_reset: Timestamp when daily quota was last reset.
    :type last_quota_reset: datetime.date
    """

    ROLE_STUDENT = "etudiant"
    ROLE_DECISION_MAKER = "decideur"
    ROLE_ADMIN = "doyen"

    ROLE_CHOICES = [
        (ROLE_STUDENT, "Étudiant / Chercheur"),
        (ROLE_DECISION_MAKER, "Décideur / Analyste"),
        (ROLE_ADMIN, "Doyen / Administrateur"),
    ]

    QUOTA_LIMITS = {
        ROLE_STUDENT: 50,
        ROLE_DECISION_MAKER: 250,
        ROLE_ADMIN: 1000,
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    daily_quota = models.IntegerField(default=50)
    tokens_used_today = models.IntegerField(default=0)
    last_quota_reset = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        """
        Override save to automatically set default daily_quota based on chosen role.

        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :returns: None
        :rtype: None

        :Example:

        >>> profile.role = 'decideur'
        >>> profile.save()
        """
        if not self.pk or self.daily_quota == 50:
            self.daily_quota = self.QUOTA_LIMITS.get(self.role, 50)
        super().save(*args, **kwargs)

    def check_and_reset_quota(self) -> None:
        """
        Check if the date has changed and reset the daily counter if necessary.

        :returns: None
        :rtype: None

        :Example:

        >>> profile.check_and_reset_quota()
        """
        today = timezone.now().date()
        last_reset = self.last_quota_reset
        if hasattr(last_reset, "date") and callable(getattr(last_reset, "date")):
            last_reset = last_reset.date()
        if last_reset < today:
            self.tokens_used_today = 0
            self.last_quota_reset = today
            self.save(update_fields=["tokens_used_today", "last_quota_reset"])

    def can_make_request(self) -> bool:
        """
        Check if the user has remaining daily quota to issue AI queries.

        :returns: True if user can execute request, False otherwise.
        :rtype: bool

        :Example:

        >>> profile.can_make_request()
        True
        """
        self.check_and_reset_quota()
        return self.tokens_used_today < self.daily_quota

    def increment_usage(self, count: int = 1) -> None:
        """
        Increment the user's daily token/request counter by specified count.

        :param count: Number of requests to add (default 1).
        :type count: int
        :returns: None
        :rtype: None

        :Example:

        >>> profile.increment_usage(1)
        """
        self.check_and_reset_quota()
        self.tokens_used_today += count
        self.save(update_fields=["tokens_used_today"])

    def get_remaining_quota(self) -> int:
        """
        Calculate remaining quota available for today.

        :returns: Number of remaining allowed queries.
        :rtype: int

        :Example:

        >>> profile.get_remaining_quota()
        49
        """
        self.check_and_reset_quota()
        return max(0, self.daily_quota - self.tokens_used_today)

    def __str__(self) -> str:
        """
        String representation of UserProfile.

        :returns: Formatted profile string.
        :rtype: str

        :Example:

        >>> str(profile)
        'test_user (Étudiant / Chercheur) - 0/50'
        """
        return f"{self.user.username} ({self.get_role_display()}) - {self.tokens_used_today}/{self.daily_quota}"
