"""
URL routing configuration for authentication module.

:Example:

>>> from django.urls import reverse
>>> print(reverse('login'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('google/callback/', views.google_oauth_callback, name='google_callback'),
]
