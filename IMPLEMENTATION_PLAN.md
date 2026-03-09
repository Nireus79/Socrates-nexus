# Socrates Nexus Implementation Plan

**Goal**: Build Phase 1 of Socrates ecosystem - a universal multi-LLM client extracted from Socrates platform.

**Timeline**: 10-14 days to initial working version
**Strategy**: Extract production patterns from Socrates, add missing features (retry, streaming), build multi-provider abstraction

---

## What We're Building

A production-ready Python library that provides a unified interface for multiple LLM providers (Anthropic, OpenAI, Google, Ollama) with automatic retry logic, token tracking, streaming support, and caching.

**Key differentiation**: Most LLM clients only work with one provider. Socrates Nexus works with ANY LLM using the same API, with production patterns built-in.

---

## Source Materials (Socrates Repository)

### Files to Extract:
1. **ClaudeClient** (`C:\Users\themi\PycharmProjects\Socrates\socratic_system\clients\claude_client.py`) - 2,457 lines
   - Lines 32-73: Lazy client initialization pattern
   - Lines 110-239: API key encryption/decryption (SHA256-Fernet, PBKDF2-Fernet, Base64)
   - Lines 335-427: Core chat method pattern
   - Lines 1674-1718: Token tracking, cost calculation, caching
   - Lines 1720-1750: JSON response parsing with markdown cleanup

2. **TTL Cache** (`C:\Users\themi\PycharmProjects\Socrates\socratic_system\utils\ttl_cache.py`) - 203 lines
   - **Copy entire file** - production-ready, thread-safe, perfect for caching

3. **Provider Models** (`C:\Users\themi\PycharmProjects\Socrates\socratic_system\models\llm_provider.py`)
   - Lines 127-229: ProviderMetadata with pricing for all providers
   - Pricing data: Claude ($0.80/$4.00 per 1M), OpenAI, Gemini, Ollama (free)

4. **Exceptions** (`C:\Users\themi\PycharmProjects\Socrates\socratic_system\exceptions\errors.py`)
   - Lines 8-44: SocratesError base class pattern

### Findings from Exploration:
- ✅ **Good patterns**: Dual sync/async, API key encryption, response caching, token tracking, cost calculation
- ❌ **Missing**: Retry logic (config exists but no implementation), streaming support (completely absent)
- ⚠️ **Coupled**: Tightly integrated with orchestrator (system_monitor, event_emitter, database, vector_db)

---

## Implementation Plan (14 Days)

### Phase 1: Foundation (Days 1-3)

#### Day 1: Core Models & Exceptions
**Files**: `exceptions.py`, `models.py`

**exceptions.py**:
- Extract base NexusError pattern from Socrates `SocratesError`
- Add specific exceptions (missing in Socrates):
  - `RateLimitError` (HTTP 429, include retry_after)
  - `AuthenticationError` (HTTP 401/403)
  - `TimeoutError` (request timeout)
  - `ProviderError` (provider-specific errors)
  - `InvalidRequestError` (malformed requests)
  - `ModelNotFoundError` (model doesn't exist)

**models.py**:
- Extract pricing data from `llm_provider.py` lines 127-229
- Create `ProviderPricing` dictionary with all provider costs
- Enhance `TokenUsage` model: add provider, model, latency_ms, timestamp
- Keep `ChatResponse`, `LLMConfig`, `UsageStats` from current stubs
- Add `StreamConfig` for streaming settings

**Reference files**:
- `C:\Users\themi\PycharmProjects\Socrates\socratic_system\exceptions\errors.py`
- `C:\Users\themi\PycharmProjects\Socrates\socratic_system\models\llm_provider.py`

#### Day 2: Retry & Streaming Utilities
**Files**: `retry.py`, `streaming.py`

**retry.py** (NEW - Socrates has config but no implementation):
```python
@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

def retry_with_backoff(config: RetryConfig):
    """Decorator for exponential backoff retry"""
    # Retry on: RateLimitError, TimeoutError, server errors (5xx)
    # Calculate delay: base * (exponential_base ** attempt)
    # Add jitter: delay * (0.5 + random() * 0.5)
```

**streaming.py** (NEW - completely missing in Socrates):
```python
class StreamHandler:
    """Helper for processing streaming responses"""
    def __init__(self, on_chunk: Callable):
        self.on_chunk = on_chunk
        self.accumulated = []

class AsyncStreamHandler:
    """Async version"""
```

#### Day 3: Caching Utilities
**File**: `utils/cache.py`

**Action**: Copy `ttl_cache.py` directly from Socrates (203 lines)
- Thread-safe TTL caching
- Hit/miss statistics
- Cleanup methods
- Production-tested

**Reference**: `C:\Users\themi\PycharmProjects\Socrates\socratic_system\utils\ttl_cache.py`

---

### Phase 2: Provider Abstraction (Days 4-5)

#### Day 4: Base Provider
**File**: `providers/base.py`

Extract patterns from ClaudeClient, make abstract:
- Lazy client initialization
- Cost calculation method (from lines 1709-1718)
- Token tracking via callbacks (not orchestrator events)
- Cache key generation (SHA256 hash from lines 1674-1676)

```python
class BaseProvider(ABC):
    def __init__(self, config: LLMConfig):
        self.config = config
        self.pricing = PROVIDER_PRICING.get(config.provider, {})
        self._usage_callbacks = []

    @abstractmethod
    def chat(self, message: str, **kwargs) -> ChatResponse:
        pass

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Extract from claude_client.py lines 1709-1718"""
        pricing = self.pricing.get(self.config.model, {})
        return (input_tokens / 1000) * pricing["input"] + (output_tokens / 1000) * pricing["output"]

    def add_usage_callback(self, callback: Callable):
        """Pluggable token tracking - replaces orchestrator"""
        self._usage_callbacks.append(callback)
```

#### Day 5: Anthropic Provider
**File**: `providers/anthropic.py`

**Extract heavily from ClaudeClient**:

1. **Client initialization** (lines 32-73):
   - Lazy `self._client` and `self._async_client`
   - Property-based access

2. **Chat method** (pattern from lines 335-427):
   - Add @retry_with_backoff decorator (NEW)
   - Call `client.messages.create()`
   - Extract usage from response
   - Calculate cost
   - Notify callbacks (replaces orchestrator)
   - Return ChatResponse

3. **Streaming** (NEW - add `stream=True`):
   ```python
   def stream(self, message: str, on_chunk: Callable, **kwargs) -> ChatResponse:
       handler = StreamHandler(on_chunk)
       with self.client.messages.stream(...) as stream:
           for text in stream.text_stream:
               handler.handle_chunk(text)
       # Extract usage from final message
   ```

4. **JSON parsing** (extract from lines 1720-1750):
   - Helper method for structured outputs
   - Handle markdown code fences

**Simplifications**:
- Remove orchestrator dependencies (system_monitor, event_emitter, database, vector_db, context_analyzer)
- Remove project-specific models (ProjectContext, ConflictInfo)
- Use callbacks instead of events
- Focus on core chat/stream methods (skip 30+ specialized methods initially)

---

### Phase 3: Additional Providers (Days 6-8)

#### Day 6: OpenAI Provider
**File**: `providers/openai.py`

Similar structure to Anthropic, adapt to OpenAI SDK:
- Use `openai.OpenAI(api_key=...)` client
- Map `chat.completions.create()` to ChatResponse
- Usage: `response.usage.prompt_tokens`, `completion_tokens`
- Streaming: `client.chat.completions.create(stream=True)`

#### Day 7: Google Provider
**File**: `providers/google.py`

Adapt for Google Generative AI SDK:
- Use `google.generativeai` client
- Map Gemini response to ChatResponse
- Different usage reporting structure

#### Day 8: Ollama Provider
**File**: `providers/ollama.py`

Local model support:
- Use `ollama` Python client
- No cost calculation (local = free)
- Support custom base_url (default: http://localhost:11434)

---

### Phase 4: Main Client Interfaces (Days 9-10)

#### Day 9: Synchronous Client
**File**: `client.py`

Extract caching pattern from ClaudeClient:
- Provider factory (select provider based on config)
- Setup usage callback for self-tracking
- Optional TTL cache for responses (lines 74-80, 1674-1676)
- Cache key generation with SHA256

```python
class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None, **kwargs):
        self.config = config or LLMConfig(...)
        self.usage_stats = UsageStats()
        self._provider = self._create_provider()
        self._provider.add_usage_callback(self._track_usage)

        if config.cache_responses:
            from .utils.cache import TTLCache
            self._cache = TTLCache(ttl_minutes=config.cache_ttl / 60)

    def chat(self, message: str, **kwargs) -> ChatResponse:
        # Check cache
        # Call provider
        # Store in cache
```

#### Day 10: Async Client
**File**: `async_client.py`

Mirror sync client structure, use async methods from providers

---

### Phase 5: Utilities & Polish (Days 11-12)

#### Day 11: Helper Utilities
**Files**: `utils/encryption.py`, `utils/parsers.py`

**encryption.py** - Extract from ClaudeClient lines 152-239:
- `encrypt_api_key()` - SHA256-Fernet encryption
- `decrypt_api_key()` - Multi-method decryption (SHA256, PBKDF2, Base64)
- Optional feature for users who want to store keys

**parsers.py** - Extract from lines 1720-1750:
- `parse_json_response()` - Handle markdown code fences, find JSON arrays/objects

#### Day 12: Examples & Documentation
**Files**: `examples/*.py`, update `README.md`

Create working examples:
1. `01_anthropic_claude.py` - Basic usage
2. `02_openai_gpt4.py` - OpenAI usage
3. `03_google_gemini.py` - Google usage
4. `04_ollama_local.py` - Local models
5. `05_streaming.py` - Streaming with callbacks
6. `06_async_calls.py` - Async usage
7. `07_token_tracking.py` - Usage tracking
8. `08_multi_model_fallback.py` - Provider fallback
9. `09_caching.py` - Response caching

Update README with comprehensive usage guide.

---

### Phase 6: Testing (Days 13-14)

#### Day 13: Unit Tests
**Directory**: `tests/`

- `test_models.py` - TokenUsage, cost calculation
- `test_retry.py` - Exponential backoff logic
- `test_exceptions.py` - Exception hierarchy
- `test_cache.py` - TTL cache behavior
- `test_base_provider.py` - Cost calculation, callbacks

#### Day 14: Integration Tests (Optional - require API keys)
- `test_anthropic_integration.py` - Real API calls
- `test_openai_integration.py` - Real API calls
- Mark with `@pytest.mark.requires_api`

---

## Key Design Decisions

### 1. Break Orchestrator Dependencies

**Current Socrates**:
```python
self.orchestrator.system_monitor.process({...})
self.orchestrator.event_emitter.emit(EventType.TOKEN_USAGE, {...})
self.orchestrator.database.get_api_key(user_id)
```

**Socrates Nexus**:
```python
# Callback pattern for tracking
provider.add_usage_callback(lambda usage: print(f"Cost: ${usage.cost_usd}"))

# Direct API key in config
config = LLMConfig(api_key="sk-ant-...")
```

### 2. What to Extract vs Rebuild

**Extract (production-tested)**:
- ✅ TTL cache decorator (copy entire file)
- ✅ API key encryption/decryption (simplify but keep multi-method)
- ✅ Cost calculation formulas
- ✅ JSON response parsing
- ✅ Lazy client initialization pattern
- ✅ Dual sync/async interface
- ✅ Cache key generation (SHA256)

**Rebuild (add missing features)**:
- ✅ Retry logic with exponential backoff
- ✅ Streaming support
- ✅ Provider abstraction layer
- ✅ Clean exception hierarchy
- ✅ Standalone operation (no orchestrator)

**Skip for now** (can add later):
- ❌ 30+ specialized methods (extract_insights, generate_code, etc.)
- ❌ Database integration for API keys
- ❌ Project-specific models (ProjectContext, ConflictInfo)
- ❌ Multi-auth (subscription tokens) - focus on API keys first

---

## Critical Files Reference

**Source (Socrates)**:
- `C:\Users\themi\PycharmProjects\Socrates\socratic_system\clients\claude_client.py` - Primary reference
- `C:\Users\themi\PycharmProjects\Socrates\socratic_system\utils\ttl_cache.py` - Copy directly
- `C:\Users\themi\PycharmProjects\Socrates\socratic_system\models\llm_provider.py` - Pricing data

**Target (Socrates Nexus)**:
- `C:\Users\themi\socrates-nexus\src\socrates_nexus\` - All implementation files

---

## Verification Strategy

### Before considering complete:
1. ✅ All 4 providers implement BaseProvider interface
2. ✅ Retry logic works (test with mock failures)
3. ✅ Streaming works for Anthropic and OpenAI
4. ✅ Token tracking via callbacks (no orchestrator)
5. ✅ Cost calculation accurate for all providers
6. ✅ Caching works (test hit/miss)
7. ✅ All 9 examples run without errors
8. ✅ Unit tests pass (75%+ coverage)
9. ✅ Type hints throughout (mypy clean)
10. ✅ README comprehensive with code examples

### Test without API keys:
- Mock provider responses
- Test retry logic with simulated failures
- Test cost calculation with known token counts
- Test caching behavior

### Test with API keys (optional):
- Real Anthropic API call
- Real OpenAI API call
- Streaming responses
- Token tracking accuracy

---

## Success Criteria

### Minimum viable implementation:
- ✅ 4 providers: Anthropic, OpenAI, Google, Ollama
- ✅ Sync + async support
- ✅ Retry with exponential backoff
- ✅ Streaming with callbacks
- ✅ Token tracking and cost calculation
- ✅ Response caching (optional feature)
- ✅ 9 working examples
- ✅ Type hints throughout
- ✅ No orchestrator dependencies

### Quality bar:
- Clean abstraction (easy to add new providers)
- Production patterns from Socrates preserved
- Simple API (5-line usage example)
- Comprehensive documentation
- Ready for PyPI publishing

---

## Implementation Order Summary

1. **Days 1-3**: Foundation (exceptions, models, retry, streaming, cache utilities)
2. **Days 4-5**: Provider abstraction (base provider, Anthropic provider)
3. **Days 6-8**: Additional providers (OpenAI, Google, Ollama)
4. **Days 9-10**: Main clients (sync client, async client)
5. **Days 11-12**: Utilities & examples (encryption, parsers, 9 examples, docs)
6. **Days 13-14**: Testing (unit tests, integration tests)

**Total**: 14 days to production-ready v0.1.0

---

## Next Actions (When Approved)

1. Start with Day 1: Create `exceptions.py` and `models.py`
2. Extract pricing data from Socrates
3. Add specific exception classes (RateLimitError, etc.)
4. Enhance TokenUsage model
5. Continue sequentially through the plan
