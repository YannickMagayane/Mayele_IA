"""
URL configuration for Congo Intelligence Hub project.

:Example:

>>> from django.urls import reverse
>>> print(reverse('chat'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    """
    Redirect root URL request to chat interface.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: HTTP Redirect response.
    :rtype: django.http.HttpResponseRedirect

    :Example:

    >>> response = root_redirect(request)
    """
    return redirect('chat')

from analyzer.views import service_worker_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker_view, name='service_worker'),
    path('auth/', include('authentication.urls')),
    path('', include('analyzer.urls')),
]
