"""
App configuration for authentication module.

:Example:

>>> from authentication.apps import AuthenticationConfig
>>> print(AuthenticationConfig.name)
'authentication'
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Django AppConfig for authentication app.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
