#!/usr/bin/env python
"""
Database Initialization Script without Migration Execution.

This script creates database tables directly using Django's connection schema editor,
checking for table existence first to prevent OperationalError on existing indexes,
strictly adhering to the rule prohibiting database migrations.

:Example:

>>> python bin/init_db.py
"""

import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from authentication.models import UserProfile
from analyzer.models import KnowledgeSource, TriangulatedFact, ChatMessage, MacroEconomicMetric


def init_tables():
    """
    Initialize database schema tables safely without executing migrations.

    :returns: None
    :rtype: None

    :Example:

    >>> init_tables()
    """
    models = [
        User,
        UserProfile,
        Session,
        ContentType,
        KnowledgeSource,
        TriangulatedFact,
        ChatMessage,
        MacroEconomicMetric,
    ]

    existing_tables = connection.introspection.table_names()

    for model in models:
        table_name = model._meta.db_table
        if table_name not in existing_tables:
            try:
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(model)
                print(f"[+] Table created for model: {model.__name__} ({table_name})")
            except Exception as exc:
                print(f"[*] Model {model.__name__} table creation warning: {exc}")
        else:
            print(f"[*] Model {model.__name__} table '{table_name}' already exists.")

    # Seed default Admin / Doyen user if not existing
    if not User.objects.filter(username="admin").exists():
        admin_user = User.objects.create_superuser("admin", "admin@rdc.cd", "admin2026")
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={"role": UserProfile.ROLE_ADMIN, "daily_quota": 1000}
        )
        print("[+] Created default superuser 'admin' (password: admin2026)")

    # Seed sample user for testing
    if not User.objects.filter(username="chercheur").exists():
        test_user = User.objects.create_user("chercheur", "chercheur@rdc.cd", "password123")
        UserProfile.objects.get_or_create(
            user=test_user,
            defaults={"role": UserProfile.ROLE_STUDENT, "daily_quota": 50}
        )
        print("[+] Created default student user 'chercheur' (password: password123)")

    # Seed initial data for RAG and Observatory
    if not TriangulatedFact.objects.exists():
        TriangulatedFact.objects.create(
            entity_name="Glencore KCC",
            territory="Kolwezi",
            topic="Emploi & Investissements",
            summary="Recrutement de 200 ingénieurs polytechniciens et techniciens supérieurs à Kolwezi.",
            verification_status="verified",
            confidence_score=0.98
        )
        TriangulatedFact.objects.create(
            entity_name="Ivanhoe Mines Kamoa",
            territory="Kolwezi",
            topic="Capacité Industrielle",
            summary="Extension des infrastructures d'extraction et de traitement de minerai de cuivre.",
            verification_status="verified",
            confidence_score=0.99
        )
        print("[+] Seeded initial Triangulated Facts")

    if not MacroEconomicMetric.objects.exists():
        for terr, sec, jobs, idx in [
            ("Kolwezi", "Mines", 185, 9.2),
            ("Lubumbashi", "Mines", 110, 8.4),
            ("Kinshasa", "Infrastructure", 95, 7.8),
            ("Goma", "Numérique", 60, 6.5)
        ]:
            MacroEconomicMetric.objects.create(
                territory=terr,
                sector=sec,
                job_offers_count=jobs,
                investment_index=idx
            )
        print("[+] Seeded MacroEconomic Metrics")


    # Register migrations in django_migrations table (Rule 23: Direct schema init, no migration DDL execution)
    try:
        from django.core.management import call_command
        call_command("migrate", "--fake", "--noinput")
        print("[+] Migrations registered in database as applied (fake mode).")
    except Exception as exc:
        print(f"[*] Migration fake-registration status: {exc}")


if __name__ == "__main__":
    init_tables()
