"""
Isolated Unit Tests for Analyzer & RAG Cognitive Router Engine.

:Example:

>>> from analyzer.tests import RAGEngineTestCase
>>> test = RAGEngineTestCase()
"""

from django.test import TestCase
from analyzer.vector_engine import VectorEngine
from analyzer.rag_engine import RAGEngine
from analyzer.models import TriangulatedFact, MacroEconomicMetric


class RAGEngineTestCase(TestCase):
    """
    Test suite for VectorEngine similarity queries and RAG truth triangulation.
    """

    def setUp(self):
        """
        Set up test database facts.

        :returns: None
        :rtype: None

        :Example:

        >>> self.setUp()
        """
        TriangulatedFact.objects.create(
            entity_name="Ivanhoe Mines",
            territory="Kolwezi",
            topic="Extraction Cuivres",
            summary="Recrutement massif à Kolwezi",
            verification_status="verified"
        )
        MacroEconomicMetric.objects.create(
            territory="Kolwezi",
            sector="Mines",
            job_offers_count=150,
            investment_index=9.5
        )

    def test_vector_engine_embedding(self):
        """
        Verify VectorEngine returns 1536-dimensional float vector.

        :returns: None
        :rtype: None

        :Example:

        >>> self.test_vector_engine_embedding()
        """
        engine = VectorEngine(collection_name="test_coll")
        vec = engine.generate_embedding("Test Query RDC")
        self.assertEqual(len(vec), 1536)

    def test_rag_triangulation(self):
        """
        Verify RAGEngine executes search and returns synthetic response with citations.

        :returns: None
        :rtype: None

        :Example:

        >>> self.test_rag_triangulation()
        """
        rag = RAGEngine()
        res = rag.execute_query("Recrutement Ivanhoe Kolwezi", user_role="etudiant")
        self.assertIn("answer", res)
        self.assertIn("Kolwezi", res["answer"])
