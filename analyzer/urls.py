"""
URL routing configuration for analyzer RAG & dashboard module.

:Example:

>>> from django.urls import reverse
>>> print(reverse('chat'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('chat/query/', views.chat_query_view, name='chat_query'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
