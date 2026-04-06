"""Tests for vision processing module."""

import pytest
from socrates_nexus.vision import VisionMessage, VisionProcessor


class TestVisionMessage:
    """Test VisionMessage class."""

    def test_creation_text_only(self):
        """Test creating vision message with text only."""
        msg = VisionMessage(text="Hello world")
        assert msg.text == "Hello world"
        assert msg.images is None or len(msg.images) == 0

    def test_creation_with_images(self):
        """Test creating vision message with images."""
        images = ["image1.png", "image2.jpg"]
        msg = VisionMessage(text="Look at these images", images=images)
        assert msg.text == "Look at these images"
        assert msg.images == images

    def test_add_image(self):
        """Test adding image to vision message."""
        msg = VisionMessage(text="Test")
        msg.add_image("test_image.png")

        assert msg.images is not None
        assert len(msg.images) > 0

    def test_image_count(self):
        """Test getting image count."""
        msg = VisionMessage(text="Images", images=["img1.png", "img2.jpg", "img3.webp"])
        count = len(msg.images)

        assert count == 3

    def test_has_images(self):
        """Test checking if vision message has images."""
        msg_with_images = VisionMessage(text="Test", images=["image.png"])
        msg_without_images = VisionMessage(text="Test only")

        assert msg_with_images.images and len(msg_with_images.images) > 0
        assert not msg_without_images.images or len(msg_without_images.images) == 0

    def test_empty_text_with_images(self):
        """Test vision message with images but no text."""
        msg = VisionMessage(images=["image.png"])
        assert msg.images is not None
        assert len(msg.images) > 0


class TestVisionProcessor:
    """Test VisionProcessor class."""

    def test_prepare_image_url(self):
        """Test preparing image from URL."""
        url = "https://example.com/image.jpg"
        result = VisionProcessor.prepare_image(url, detail="high")

        assert result is not None
        assert hasattr(result, "source")
        assert hasattr(result, "media_type")

    def test_prepare_image_local_path(self):
        """Test preparing image from local path."""
        # Use a test that doesn't require actual files
        path = "test_image.png"
        result = VisionProcessor.prepare_image(path, detail="low")

        assert result is not None

    def test_is_image_url(self):
        """Test checking if string is image URL."""
        url = "https://example.com/image.jpg"
        result = VisionProcessor.is_image_url(url)

        assert isinstance(result, bool)

    def test_is_image_path(self):
        """Test checking if string is image file path."""
        path = "image.png"
        result = VisionProcessor.is_image_path(path)

        assert isinstance(result, bool)

    def test_image_detail_levels(self):
        """Test different image detail levels."""
        url = "https://example.com/image.jpg"

        result_high = VisionProcessor.prepare_image(url, detail="high")
        result_low = VisionProcessor.prepare_image(url, detail="low")

        assert result_high is not None
        assert result_low is not None

    def test_supported_image_formats(self):
        """Test getting supported image formats."""
        formats = VisionProcessor.get_supported_formats()

        assert isinstance(formats, list)
        assert len(formats) > 0
        assert "jpg" in formats or "jpeg" in formats or "png" in formats

    def test_validate_image(self):
        """Test image validation."""
        valid_url = "https://example.com/image.png"
        result = VisionProcessor.validate_image(valid_url)

        assert isinstance(result, bool)

    def test_batch_process_images(self):
        """Test batch processing multiple images."""
        images = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.png",
        ]

        results = VisionProcessor.batch_process(images, detail="high")

        assert isinstance(results, list)

    def test_image_metadata(self):
        """Test extracting image metadata."""
        url = "https://example.com/image.jpg"
        image = VisionProcessor.prepare_image(url, detail="high")

        # Should have metadata attributes
        assert hasattr(image, "source")
        assert hasattr(image, "media_type")

    def test_format_for_api(self):
        """Test formatting image for API request."""
        url = "https://example.com/image.jpg"
        image = VisionProcessor.prepare_image(url, detail="high")

        formatted = VisionProcessor.format_for_api(image, api_format="openai")

        assert isinstance(formatted, dict) or formatted is not None

    def test_validate_vision_message(self):
        """Test validating vision message."""
        msg = VisionMessage(text="Test", images=["image.png"])
        result = VisionProcessor.validate_vision_message(msg)

        assert isinstance(result, bool)


class TestVisionIntegration:
    """Integration tests for vision functionality."""

    def test_vision_message_roundtrip(self):
        """Test creating and using vision message."""
        msg = VisionMessage(
            text="Analyze these images",
            images=["img1.jpg", "img2.png"]
        )

        assert msg.text == "Analyze these images"
        assert len(msg.images) == 2

    def test_prepare_and_format_image(self):
        """Test full image preparation and formatting."""
        url = "https://example.com/image.jpg"

        # Prepare
        prepared = VisionProcessor.prepare_image(url, detail="high")
        assert prepared is not None

        # Format for API
        formatted = VisionProcessor.format_for_api(prepared, api_format="openai")
        assert formatted is not None or isinstance(formatted, dict)

    def test_multiple_image_formats(self):
        """Test handling multiple image formats."""
        images = {
            "jpg": "https://example.com/photo.jpg",
            "png": "https://example.com/graphic.png",
            "webp": "https://example.com/modern.webp",
            "gif": "https://example.com/animation.gif",
        }

        for fmt, url in images.items():
            result = VisionProcessor.prepare_image(url, detail="low")
            assert result is not None
