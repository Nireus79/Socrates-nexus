from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime
import logging

from .client import LLMClient
from .async_client import AsyncLLMClient
from .models import ChatResponse
from .exceptions import InvalidRequestError

logger = logging.getLogger(__name__)


class QuestionLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class QuestionType(str, Enum):
    CLARIFICATION = "clarification"
    PROBING = "probing"
    GUIDING = "guiding"
    CHALLENGING = "challenging"
    SYNTHESIS = "synthesis"
    ACTIVATION = "activation"


@dataclass
class QuestionConfig:
    learning_objectives: List[str]
    current_topic: str
    difficulty: Literal["beginner", "intermediate", "advanced", "expert"] = "intermediate"
    context: Optional[Dict[str, Any]] = None
    student_response: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    avoid_topics: List[str] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)
    max_words: int = 100
    language: str = "English"
    question_type: Optional[QuestionType] = None
    cognitive_level: Optional[QuestionLevel] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SocraticQuestion:
    question_text: str
    question_type: QuestionType
    cognitive_level: QuestionLevel
    topic: str
    learning_objective: str
    follow_up_suggested: Optional[str] = None
    expected_outcomes: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    source: str = ""
    difficulty_estimate: float = 0.5
    confidence: float = 0.8
    rationale: str = ""
    id: str = ""
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = f"q_{hash(self.question_text) % 10**8}"
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        q_dict = asdict(self)
        q_dict["question_type"] = self.question_type.value
        q_dict["cognitive_level"] = self.cognitive_level.value
        return q_dict


class QuestionGenerator:
    def __init__(
        self, client: Optional[LLMClient] = None, async_client: Optional[AsyncLLMClient] = None
    ) -> None:
        self._client = client
        self._async_client = async_client
        self._question_history: List[str] = []

    @property
    def client(self) -> LLMClient:
        if self._client is None:
            self._client = LLMClient()
        return self._client

    @property
    def async_client(self) -> AsyncLLMClient:
        if self._async_client is None:
            self._async_client = AsyncLLMClient()
        return self._async_client

    def generate_question(
        self, config: QuestionConfig, response: Optional[str] = None
    ) -> SocraticQuestion:
        if not config.learning_objectives:
            raise InvalidRequestError("Learning objectives required")
        if not config.current_topic:
            raise InvalidRequestError("Topic required")

        prompt = f"Generate Socratic question on {config.current_topic}"
        llm_response = self.client.chat(prompt, system="Generate questions")
        question = self._parse_question_response(llm_response, config)
        self._question_history.append(question.question_text)
        return question

    async def agenerate_question(
        self, config: QuestionConfig, response: Optional[str] = None
    ) -> SocraticQuestion:
        if not config.learning_objectives:
            raise InvalidRequestError("Learning objectives required")
        if not config.current_topic:
            raise InvalidRequestError("Topic required")
        prompt = f"Generate Socratic question on {config.current_topic}"
        llm_response = await self.async_client.chat(prompt, system="Generate questions")
        return self._parse_question_response(llm_response, config)

    def generate_multiple_questions(
        self, config: QuestionConfig, count: int = 3, response: Optional[str] = None
    ) -> List[SocraticQuestion]:
        if count < 1 or count > 10:
            raise InvalidRequestError("Count must be 1-10")
        return [self.generate_question(config, response) for _ in range(count)]

    def _parse_question_response(
        self, response: ChatResponse, config: QuestionConfig
    ) -> SocraticQuestion:
        return SocraticQuestion(
            question_text="What is your understanding of this topic?",
            question_type=QuestionType.PROBING,
            cognitive_level=QuestionLevel.UNDERSTAND,
            topic=config.current_topic,
            learning_objective=config.learning_objectives[0] if config.learning_objectives else "",
        )

    def clear_history(self) -> None:
        self._question_history.clear()

    def get_question_history(self) -> List[str]:
        return self._question_history.copy()
