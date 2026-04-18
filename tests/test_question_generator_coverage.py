
from socrates_nexus.question_generator import (
    QuestionLevel, QuestionType, QuestionConfig, SocraticQuestion, QuestionGenerator
)

class TestQuestionLevel:
    def test_levels(self):
        levels = [
            QuestionLevel.REMEMBER, QuestionLevel.UNDERSTAND, QuestionLevel.APPLY,
            QuestionLevel.ANALYZE, QuestionLevel.EVALUATE, QuestionLevel.CREATE,
        ]
        assert len(levels) == 6

class TestQuestionType:
    def test_types(self):
        types = [
            QuestionType.CLARIFICATION, QuestionType.PROBING, QuestionType.GUIDING,
            QuestionType.CHALLENGING, QuestionType.SYNTHESIS, QuestionType.ACTIVATION,
        ]
        assert len(types) == 6

class TestQuestionConfig:
    def test_creation(self):
        c = QuestionConfig(learning_objectives=["test"], current_topic="test")
        assert c.learning_objectives == ["test"]

class TestSocraticQuestion:
    def test_creation(self):
        q = SocraticQuestion(text="q?", level=QuestionLevel.REMEMBER, question_type=QuestionType.CLARIFICATION)
        assert q.text == "q?"

class TestQuestionGenerator:
    def test_init(self):
        gen = QuestionGenerator()
        assert gen is not None
