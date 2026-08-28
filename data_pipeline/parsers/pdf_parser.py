"""
Semantic PDF Parser for Books, Academic Syllabuses, and Official Decrees.

This module extracts text content from PDF files and splits long documents into
semantic chunks suitable for vector store embedding.

:Example:

>>> from data_pipeline.parsers.pdf_parser import PDFParser
>>> parser = PDFParser()
>>> chunks = parser.parse_text_chunks("Contenu d'ordonnance officielle du gouvernement RDC...")
>>> print(len(chunks))
1
"""

import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """
    Parser for converting PDF document content into semantic text chunks.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        """
        Initialize PDFParser chunking parameters.

        :param chunk_size: Character length of each chunk.
        :type chunk_size: int
        :param chunk_overlap: Overlap length between adjacent chunks.
        :type chunk_overlap: int
        :returns: None
        :rtype: None

        :Example:

        >>> parser = PDFParser(chunk_size=800)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def parse_text_chunks(self, text: str) -> list:
        """
        Split raw extracted PDF text into overlapping semantic chunks.

        :param text: Raw document text string.
        :type text: str
        :returns: List of text chunk strings.
        :rtype: list

        :Example:

        >>> parser = PDFParser()
        >>> chunks = parser.parse_text_chunks("Article 1: Le présent décret règle...")
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks
