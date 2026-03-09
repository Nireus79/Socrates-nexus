"""Streaming helpers for Socrates Nexus."""

from typing import Callable, Optional, List


class StreamHandler:
    """Handler for streaming responses."""

    def __init__(self, on_chunk: Optional[Callable[[str], None]] = None):
        """
        Initialize stream handler.

        Args:
            on_chunk: Optional callback for each chunk
        """
        self.on_chunk = on_chunk
        self.chunks: List[str] = []
        self.complete = False

    def handle_chunk(self, chunk: str) -> None:
        """Handle a chunk from the stream."""
        if chunk:
            self.chunks.append(chunk)
            if self.on_chunk:
                try:
                    self.on_chunk(chunk)
                except Exception:
                    # Don't fail the stream if callback fails
                    pass

    def get_complete_response(self) -> str:
        """Get the complete accumulated response."""
        return "".join(self.chunks)

    def clear(self) -> None:
        """Clear accumulated chunks."""
        self.chunks = []

    def finish(self) -> str:
        """Mark stream as complete and return full response."""
        self.complete = True
        return self.get_complete_response()


class StreamBuffer:
    """Alias for StreamHandler for backwards compatibility."""

    def __init__(self, on_chunk: Optional[Callable[[str], None]] = None):
        """
        Initialize stream buffer.

        Args:
            on_chunk: Optional callback for each chunk
        """
        self._handler = StreamHandler(on_chunk)

    def add_chunk(self, chunk: str) -> None:
        """Add a chunk to the buffer."""
        self._handler.handle_chunk(chunk)

    def get_complete(self) -> str:
        """Get the complete buffered content."""
        return self._handler.get_complete_response()

    def clear(self) -> None:
        """Clear the buffer."""
        self._handler.clear()


class AsyncStreamHandler:
    """Handler for async streaming responses."""

    def __init__(self, on_chunk: Optional[Callable[[str], None]] = None):
        """
        Initialize async stream handler.

        Args:
            on_chunk: Optional async callback for each chunk
        """
        self.on_chunk = on_chunk
        self.chunks: List[str] = []
        self.complete = False

    async def handle_chunk(self, chunk: str) -> None:
        """Handle a chunk from the async stream."""
        if chunk:
            self.chunks.append(chunk)
            if self.on_chunk:
                try:
                    # Support both async and sync callbacks
                    if callable(self.on_chunk):
                        import inspect

                        if inspect.iscoroutinefunction(self.on_chunk):
                            await self.on_chunk(chunk)
                        else:
                            self.on_chunk(chunk)
                except Exception:
                    # Don't fail the stream if callback fails
                    pass

    def get_complete_response(self) -> str:
        """Get the complete accumulated response."""
        return "".join(self.chunks)

    def clear(self) -> None:
        """Clear accumulated chunks."""
        self.chunks = []

    async def finish(self) -> str:
        """Mark stream as complete and return full response."""
        self.complete = True
        return self.get_complete_response()
