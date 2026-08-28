"""
Isolated Unit Tests for Authentication & Quota Management App.

:Example:

>>> from authentication.tests import UserQuotaTestCase
>>> test = UserQuotaTestCase()
"""

from django.test import TestCase
from django.contrib.auth.models import User
from authentication.models import UserProfile


class UserQuotaTestCase(TestCase):
    """
    Test suite verifying role-based user quota limits and usage tracking.
    """

    def setUp(self):
        """
        Set up test users and profiles.

        :returns: None
        :rtype: None

        :Example:

        >>> self.setUp()
        """
        self.user = User.objects.create_user(username="student_user", password="password123")
        self.profile = UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_STUDENT)

    def test_student_quota_limit(self):
        """
        Verify student role gets 50 daily requests.

        :returns: None
        :rtype: None

        :Example:

        >>> self.test_student_quota_limit()
        """
        self.assertEqual(self.profile.daily_quota, 50)
        self.assertTrue(self.profile.can_make_request())

    def test_quota_increment_and_exhaustion(self):
        """
        Verify incrementing quota usage updates remaining counter and enforces limits.

        :returns: None
        :rtype: None

        :Example:

        >>> self.test_quota_increment_and_exhaustion()
        """
        self.profile.increment_usage(50)
        self.assertEqual(self.profile.tokens_used_today, 50)
        self.assertFalse(self.profile.can_make_request())
        self.assertEqual(self.profile.get_remaining_quota(), 0)
