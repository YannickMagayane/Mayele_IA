"""
Analyzer Views Module.

Provides views for the HTMX-driven RAG chat interface and the macroeconomic analytics dashboard.

:Example:

>>> from django.test import RequestFactory
>>> factory = RequestFactory()
>>> request = factory.get('/')
>>> response = chat_view(request)
"""

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Avg
from django.utils import timezone
from authentication.models import UserProfile
from .models import ChatMessage, KnowledgeSource, TriangulatedFact, MacroEconomicMetric
from .rag_engine import RAGEngine

rag_engine = RAGEngine()


GUEST_DAILY_QUOTA = 50


def _get_guest_quota(request) -> tuple[int, int, int]:
    """
    Retrieve or initialize session-based quota tracking for unauthenticated guests.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: Tuple of (remaining_quota, daily_quota, tokens_used_today).
    :rtype: tuple[int, int, int]
    """
    today_str = timezone.now().strftime("%Y-%m-%d")
    last_date = request.session.get("guest_quota_date", "")
    if last_date != today_str:
        request.session["guest_quota_date"] = today_str
        request.session["guest_tokens_used_today"] = 0
        request.session.modified = True

    tokens_used = request.session.get("guest_tokens_used_today", 0)
    remaining_quota = max(0, GUEST_DAILY_QUOTA - tokens_used)
    return remaining_quota, GUEST_DAILY_QUOTA, tokens_used


def chat_view(request):
    """
    Render main Agentic RAG chat interface.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: Rendered HTML chat interface.
    :rtype: django.http.HttpResponse

    :Example:

    >>> response = chat_view(request)
    """
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        messages = ChatMessage.objects.filter(user=request.user).order_by("created_at")
        remaining_quota = profile.get_remaining_quota()
        daily_quota = profile.daily_quota
        tokens_used = profile.tokens_used_today
    else:
        profile = None
        messages = []
        remaining_quota, daily_quota, tokens_used = _get_guest_quota(request)

    recent_sources = KnowledgeSource.objects.all().order_by("-ingested_at")[:5]
    usage_percentage = int((tokens_used / daily_quota) * 100) if daily_quota else 0

    context = {
        "profile": profile,
        "remaining_quota": remaining_quota,
        "daily_quota": daily_quota,
        "tokens_used_today": tokens_used,
        "usage_percentage": usage_percentage,
        "messages": messages,
        "recent_sources": recent_sources,
    }
    return render(request, "analyzer/chat.html", context)


def chat_query_view(request):
    """
    HTMX Endpoint for handling RAG prompt execution (accessible to authenticated and guest users).

    Checks user quota (session-based for guests, ORM profile for authenticated users),
    runs RAGEngine triangulation, increments usage, and returns dynamic response snippet.

    :param request: HTTP Request object containing POST 'prompt'.
    :type request: django.http.HttpRequest
    :returns: HTML partial response for HTMX insertion.
    :rtype: django.http.HttpResponse

    :Example:

    >>> response = chat_query_view(request)
    """
    if request.method != "POST":
        return HttpResponse("Méthode non autorisée", status=405)

    prompt = request.POST.get("prompt", "").strip()
    if not prompt:
        return HttpResponse("", status=400)

    chat_history = []
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_role = profile.role
        if not profile.can_make_request():
            error_html = (
                "<div class='p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm font-bold'>"
                "⚠️ <strong>Quota Quotidien Épuisé :</strong> Vous avez atteint le nombre maximal de requêtes autorisées pour aujourd'hui."
                "</div>"
            )
            return HttpResponse(error_html)
        profile.increment_usage(1)
        remaining_quota = profile.get_remaining_quota()
        daily_quota = profile.daily_quota
        tokens_used = profile.tokens_used_today

        # Fetch last 5 conversation messages for multi-turn context
        past_msgs = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:5]
        for pm in reversed(list(past_msgs)):
            chat_history.append({"prompt": pm.prompt, "response": pm.response_text})
    else:
        user_role = "etudiant"
        remaining_quota, daily_quota, tokens_used = _get_guest_quota(request)
        if remaining_quota <= 0:
            error_html = (
                "<div class='p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm font-bold'>"
                "⚠️ <strong>Quota Quotidien Invité Épuisé :</strong> Vous avez atteint le quota gratuit de 50 requêtes pour aujourd'hui. "
                "Connectez-vous pour sauvegarder vos conversations et réinitialiser votre quota."
                "</div>"
            )
            return HttpResponse(error_html)

        tokens_used += 1
        request.session["guest_tokens_used_today"] = tokens_used
        request.session.modified = True
        remaining_quota = max(0, daily_quota - tokens_used)

    # Execute RAG query pipeline with multi-turn history context
    rag_result = rag_engine.execute_query(prompt, user_role=user_role, chat_history=chat_history)

    # Save to ChatMessage persistent history if user is authenticated
    if request.user.is_authenticated:
        msg = ChatMessage.objects.create(
            user=request.user,
            prompt=prompt,
            response_text=rag_result["answer"],
            citations_json=json.dumps(rag_result.get("sources", []))
        )
    else:
        msg = type("TempMsg", (), {
            "id": "guest-tmp",
            "prompt": prompt,
            "response_text": rag_result["answer"],
            "created_at": timezone.now()
        })()

    context = {
        "msg": msg,
        "citations": rag_result.get("sources", []),
        "remaining_quota": remaining_quota,
        "daily_quota": daily_quota,
        "tokens_used_today": tokens_used,
        "usage_percentage": int((tokens_used / daily_quota) * 100) if daily_quota else 0,
    }

    return render(request, "analyzer/partials/chat_message_partial.html", context)



@login_required
def dashboard_view(request):
    """
    Render Macroeconomic and Industrial Analytics Dashboard.

    Calculates aggregate job demand metrics, investment indices by territory
    (Kinshasa, Lubumbashi, Kolwezi, Goma), and facts summary.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: Rendered HTML dashboard page.
    :rtype: django.http.HttpResponse

    :Example:

    >>> response = dashboard_view(request)
    """
    metrics = MacroEconomicMetric.objects.all()

    # Aggregations by territory using Django ORM QuerySets (Rule 12: Prefer Django ORM)
    territory_stats = metrics.values("territory").annotate(
        total_jobs=Sum("job_offers_count"),
        avg_investment=Avg("investment_index")
    ).order_by("-total_jobs")

    sector_stats = metrics.values("sector").annotate(
        total_jobs=Sum("job_offers_count")
    ).order_by("-total_jobs")

    recent_facts = TriangulatedFact.objects.all().order_by("-created_at")[:10]
    total_sources = KnowledgeSource.objects.count()

    context = {
        "territory_stats": territory_stats,
        "sector_stats": sector_stats,
        "recent_facts": recent_facts,
        "total_sources": total_sources,
    }
    return render(request, "analyzer/dashboard.html", context)


def service_worker_view(request):
    """
    Serve Service Worker JavaScript file for offline PWA functionality.

    :param request: HTTP Request object.
    :type request: django.http.HttpRequest
    :returns: JavaScript Response object.
    :rtype: django.http.HttpResponse

    :Example:

    >>> response = service_worker_view(request)
    """
    sw_code = """
const CACHE_NAME = 'mayele-ia-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/auth/login/',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/htmx.org@1.9.10',
    'https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&display=swap'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
                return response;
            })
            .catch(() => caches.match(event.request).then((res) => res || caches.match('/')))
    );
});
"""
    return HttpResponse(sw_code, content_type="application/javascript")
