"""
Django Admin interface customization for UserProfile.

:Example:

>>> from authentication.admin import UserProfileAdmin
"""

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin model view for UserProfile quota management.
    """
    list_display = ("user", "role", "daily_quota", "tokens_used_today", "last_quota_reset")
    list_filter = ("role", "last_quota_reset")
    search_fields = ("user__username", "user__email")
