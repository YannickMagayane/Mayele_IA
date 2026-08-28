"""
Django settings for Congo Intelligence Hub project.

This module configures Django settings including database, authentication,
ChromaDB integration, security policies, and application apps.

:Example:

>>> from django.conf import settings
>>> print(settings.SECRET_KEY)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-congo-intelligence-hub-key-2026")

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    "authentication",
    "analyzer",
    "data_pipeline",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database Configuration (SQLite3 for Observatory RDC)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "observatory_rdc.db",
        "OPTIONS": {
            "timeout": 60,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Kinshasa"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Gemini & ChromaDB RAG Configuration
GEMINI_API_KEY_PRO = os.getenv("GEMINI_API_KEY_PRO", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_CSE_CX_ID = os.getenv("GOOGLE_CSE_CX_ID", "207212789a68643f0")

# Google CSE JSON API Key — must be a Google Cloud API Key (AIzaSy...) generated at:
# console.cloud.google.com > APIs & Services > Credentials > Create API Key
# The GOOGLE_CSE_API_KEY in .env is a GOCSPX OAuth2 secret (not valid for CSE JSON API).
# To enable: create an AIzaSy key and add GOOGLE_CSE_JSON_API_KEY=AIzaSy... to .env
GOOGLE_CSE_JSON_API_KEY = os.getenv("GOOGLE_CSE_JSON_API_KEY", "")

# Legacy key from .env — only valid for OAuth2, NOT for CSE JSON API
# Kept for backward compat, will be ignored by AutonomousLinker CSE calls
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY", "")

# CSE is enabled when a proper AIzaSy API key is configured
GOOGLE_CSE_ENABLED = GOOGLE_CSE_JSON_API_KEY.startswith("AIza")

CHROMA_DB_DIR = BASE_DIR / "chroma_db_store"
STAGING_CACHE_DIR = BASE_DIR / "data_pipeline" / "staging_cache"

# Authentication Redirection Settings
LOGIN_URL = "auth:login"
LOGIN_REDIRECT_URL = "chat"
LOGOUT_REDIRECT_URL = "chat"


