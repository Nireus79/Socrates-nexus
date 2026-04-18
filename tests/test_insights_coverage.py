import json
import pytest
from unittest.mock import Mock

from socrates_nexus.insights import Insight, InsightExtractor, InsightAnalyzer
from socrates_nexus.exceptions import InvalidRequestError
from socrates_nexus.models import ChatResponse, TextContent

class TestInsight:
    def test_insight_creation(self):
        insight = Insight(text="test", category="c", confidence=0.9, source="s")
        assert insight.text == "test"
        assert insight.confidence == 0.9

    def test_insight_clamping(self):
        i1 = Insight(text="t", category="c", confidence=1.5, source="s")
        assert i1.confidence == 1.0
        i2 = Insight(text="t", category="c", confidence=-0.5, source="s")
        assert i2.confidence == 0.0

class TestInsightExtractor:
    def test_empty_text_error(self):
        e = InsightExtractor()
        with pytest.raises(InvalidRequestError):
            e.extract_insights("")

class TestInsightAnalyzer:
    def test_empty(self):
        a = InsightAnalyzer()
        r = a.analyze_insights([])
        assert r["patterns"] == []
