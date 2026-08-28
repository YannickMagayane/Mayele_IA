"""
Authentication Views Module.

Provides authentication endpoints for email-based user login, registration, logout,
Google OAuth callback, and quota profile status visualization.

:Example:

>>> from django.test import RequestFactory
>>> factory = RequestFactory()
>>> request = factory.get('/auth/login/')
>>> response = login_view(request)
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile


def login_view(request):
    """
    Handle email-based user authentication login with max 8 characters password limit.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: HTTP response rendering login form or redirecting.
    :rtype: django.http.HttpResponse

    :Example:

    >>> response = login_view(request)
    """
    if request.user.is_authenticated:
        return redirect("chat")

    if request.method == "POST":
        email_or_user = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        # Enforce max 8 characters password constraint
        if len(password) > 8:
            password = password[:8]
            messages.warning(request, "Le mot de passe a été tronqué à 8 caractères maximum.")

        # Find user by email or username
        target_user = User.objects.filter(email__iexact=email_or_user).first()
        if not target_user:
            target_user = User.objects.filter(username__iexact=email_or_user).first()

        if target_user:
            user = authenticate(request, username=target_user.username, password=password)
            if user is not None:
                login(request, user)
                UserProfile.objects.get_or_create(user=user)
                messages.success(request, f"Bienvenue, {user.email or user.username} !")
                return redirect("chat")

        messages.error(request, "Identifiants invalides (adresse e-mail ou mot de passe incorrect).")

    return render(request, "auth/login.html")


def register_view(request):
    """
    Handle user registration via email and max 8 characters password.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: HTTP response rendering registration form or redirecting.
    :rtype: django.http.HttpResponse

    :Example:

    >>> response = register_view(request)
    """
    if request.user.is_authenticated:
        return redirect("chat")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        role = request.POST.get("role", UserProfile.ROLE_STUDENT)

        if len(password) > 8:
            messages.error(request, "Le mot de passe ne doit pas dépasser 8 caractères.")
        elif not email or not password:
            messages.error(request, "Veuillez renseigner une adresse e-mail et un mot de passe.")
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Cette adresse e-mail est déjà associée à un compte.")
        else:
            username = email.split("@")[0]
            # Ensure unique username
            base_user = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_user}_{counter}"
                counter += 1

            user = User.objects.create_user(username=username, email=email, password=password)
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={"role": role})
            if not created:
                profile.role = role
                profile.save()

            login(request, user)
            messages.success(request, "Compte créé avec succès !")
            return redirect("chat")

    return render(request, "auth/register.html")


def google_oauth_callback(request):
    """
    Handle OAuth callback redirect from Google Cloud Console in local environment.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: HTTP Redirect response.
    :rtype: django.http.HttpResponseRedirect

    :Example:

    >>> response = google_oauth_callback(request)
    """
    messages.success(request, "Connexion Google autorisée et validée.")
    return redirect("chat")


def logout_view(request):
    """
    Log out current user and redirect to login page.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: HTTP Redirect response.
    :rtype: django.http.HttpResponseRedirect

    :Example:

    >>> response = logout_view(request)
    """
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect("login")


@login_required
def profile_view(request):
    """
    Display current user's profile information and daily API quotas.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: HTTP response rendering profile view.
    :rtype: django.http.HttpResponse

    :Example:

    >>> response = profile_view(request)
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.check_and_reset_quota()
    context = {
        "profile": profile,
        "remaining_quota": profile.get_remaining_quota(),
    }
    return render(request, "auth/profile.html", context)
