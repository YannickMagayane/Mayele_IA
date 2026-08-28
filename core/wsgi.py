"""
WSGI config for Congo Intelligence Hub project.

It exposes the WSGI callable as a module-level variable named ``application``.

:Example:

>>> from core.wsgi import application
>>> print(application)
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
