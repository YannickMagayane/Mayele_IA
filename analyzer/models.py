"""
Data Models for RAG Analyzer and Cognitive Triangulation Engine.

This module defines Django models storing knowledge sources, cross-verified facts,
chat histories, and macro-economic metric indicators for the DRC Observatory.

:Example:

>>> from analyzer.models import KnowledgeSource
>>> source = KnowledgeSource.objects.create(
...     title="Journal Officiel RDC - Code Minier",
...     source_type="gazette",
...     url="https://journalofficiel.cd/decrets/2026-01"
... )
>>> print(source.title)
'Journal Officiel RDC - Code Minier'
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class KnowledgeSource(models.Model):
    """
    Model representing an ingested knowledge source item.

    :param title: Title or headline of document/media.
    :type title: str
    :param source_type: Category of source (gazette, news, mining_tender, youtube, social).
    :type source_type: str
    :param url: URL or origin location reference.
    :type url: str
    :param content: Raw text chunk content.
    :type content: str
    :param timestamp_seconds: Optional second offset for audio/video media.
    :type timestamp_seconds: int
    :param confidence_score: Reliability score calculated by triangulation (0.0 to 1.0).
    :type confidence_score: float
    :param ingested_at: Creation timestamp.
    :type ingested_at: datetime
    """

    SOURCE_TYPES = [
        ("gazette", "Journal Officiel / Décret Legistatif"),
        ("news", "Presse Internationale / RFI / France 24"),
        ("mining_tender", "Offre Industrielle (Glencore, Ivanhoe, MMG)"),
        ("youtube", "Média Audiovisuel Horodaté"),
        ("social", "Alerte X / Twitter Certifiée"),
    ]

    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, default="news")
    url = models.URLField(max_length=500, blank=True, default="")
    content = models.TextField()
    timestamp_seconds = models.IntegerField(null=True, blank=True, help_text="Audio/Video timestamp offset in seconds")
    confidence_score = models.FloatField(default=1.0)
    ingested_at = models.DateTimeField(default=timezone.now)

    def get_formatted_link(self) -> str:
        """
        Return direct clickable hyperlinked URL, formatted with second timestamp if applicable.

        :returns: Formatted link string.
        :rtype: str

        :Example:

        >>> source = KnowledgeSource(url="https://youtu.be/abc", timestamp_seconds=125)
        >>> source.get_formatted_link()
        'https://youtu.be/abc?t=125'
        """
        if self.url and self.timestamp_seconds and "youtube" in self.url:
            return f"{self.url}?t={self.timestamp_seconds}"
        return self.url or "#"

    def __str__(self) -> str:
        """
        String representation of KnowledgeSource.

        :returns: Title and source type string.
        :rtype: str

        :Example:

        >>> str(source)
        'Journal Officiel RDC - Code Minier [gazette]'
        """
        return f"{self.title} [{self.source_type}]"


class TriangulatedFact(models.Model):
    """
    Model representing structured facts cross-verified between multiple sources.

    :param entity_name: Mining company, ministry, or institution (e.g. Glencore KCC, ONEM).
    :type entity_name: str
    :param territory: DRC Region (Kinshasa, Lubumbashi, Kolwezi, Goma).
    :type territory: str
    :param topic: Category (Législation, Emploi, Investissement, Sécurité).
    :type topic: str
    :param summary: Verified factual statement.
    :type summary: str
    :param verification_status: Verification status (Verified, Contradiction, Pending).
    :type verification_status: str
    :param confidence_score: Calculated truth triangulation score (0.0 to 1.0).
    :type confidence_score: float
    :param created_at: Record creation timestamp.
    :type created_at: datetime
    """

    TERRITORIES = [
        ("Kinshasa", "Kinshasa"),
        ("Lubumbashi", "Lubumbashi (Haut-Katanga)"),
        ("Kolwezi", "Kolwezi (Lualaba)"),
        ("Goma", "Goma (Nord-Kivu)"),
        ("National", "National RDC"),
    ]

    entity_name = models.CharField(max_length=150)
    territory = models.CharField(max_length=50, choices=TERRITORIES, default="National")
    topic = models.CharField(max_length=100)
    summary = models.TextField()
    verification_status = models.CharField(
        max_length=30,
        choices=[("verified", "Vérifié"), ("contradiction", "Contradiction Temporelle"), ("rumor", "Rumeur / À vérifier")],
        default="verified"
    )
    confidence_score = models.FloatField(default=0.95)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        """
        String representation of TriangulatedFact.

        :returns: Formatted entity and territory string.
        :rtype: str

        :Example:

        >>> str(fact)
        'Glencore KCC (Kolwezi) - Verified'
        """
        return f"{self.entity_name} ({self.territory}) - {self.verification_status}"


class ChatMessage(models.Model):
    """
    Model for persistent user chat sessions and RAG responses.

    :param user: User issuing the query.
    :type user: django.contrib.auth.models.User
    :param prompt: Raw user prompt.
    :type prompt: str
    :param response_text: Synthetic RAG answer generated by agentic engine.
    :type response_text: str
    :param citations_json: JSON string storing matched citations and timestamps.
    :type citations_json: str
    :param created_at: Message creation timestamp.
    :type created_at: datetime
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_messages")
    prompt = models.TextField()
    response_text = models.TextField()
    citations_json = models.TextField(blank=True, default="[]")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        """
        String representation of ChatMessage.

        :returns: User and prompt snippet.
        :rtype: str

        :Example:

        >>> str(msg)
        'user1: Quel est le taux de recrutement à Kolwezi ?'
        """
        return f"{self.user.username}: {self.prompt[:40]}"


class MacroEconomicMetric(models.Model):
    """
    Data table for structured analytics, heatmaps, and trend charts.

    :param territory: DRC Region.
    :type territory: str
    :param sector: Industry sector (Mines, Énergie, Infrastructure, Numérique).
    :type sector: str
    :param job_offers_count: Ingested job post volume.
    :type job_offers_count: int
    :param investment_index: Calculated investment dynamic index.
    :type investment_index: float
    :param record_date: Date of metric recording.
    :type record_date: datetime.date
    """

    territory = models.CharField(max_length=50)
    sector = models.CharField(max_length=100)
    job_offers_count = models.IntegerField(default=0)
    investment_index = models.FloatField(default=0.0)
    record_date = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        """
        String representation of MacroEconomicMetric.

        :returns: Territory and sector string.
        :rtype: str

        :Example:

        >>> str(metric)
        'Kolwezi - Mines (2026-08)'
        """
        return f"{self.territory} - {self.sector} ({self.record_date})"
