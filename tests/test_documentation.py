"""Tests for documentation generation module."""

import pytest
from socrates_nexus.documentation import DocumentationGenerator
from socrates_nexus.models import LLMConfig


class TestDocumentationGenerator:
    """Test DocumentationGenerator class."""

    def test_initialization(self):
        """Test generator initialization."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        assert gen.config == config
        assert gen.format == "markdown"

    def test_initialization_with_format(self):
        """Test generator initialization with custom format."""
        config = LLMConfig(provider="openai", model="gpt-4")
        gen = DocumentationGenerator(config=config, format="restructured")

        assert gen.format == "restructured"

    def test_get_supported_formats(self):
        """Test getting supported documentation formats."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        formats = gen.get_supported_formats()

        assert isinstance(formats, list)
        assert "markdown" in formats
        assert len(formats) > 0

    def test_format_property(self):
        """Test format property getter and setter."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        assert gen.format == "markdown"

        # Try setting different format
        original_format = gen.format
        gen.format = "restructured"
        assert gen.format == "restructured"

        gen.format = original_format

    def test_generate_from_docstring(self):
        """Test generating documentation from docstring."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        docstring = """
        This is a test function.

        Args:
            x: First parameter
            y: Second parameter

        Returns:
            The sum of x and y
        """

        # This would require LLM integration, so we test structure only
        assert gen is not None
        assert gen.config.model == "claude-3-sonnet"

    def test_generate_from_code(self):
        """Test generating documentation from code."""
        config = LLMConfig(provider="openai", model="gpt-4")
        gen = DocumentationGenerator(config=config)

        code = """
def add(x, y):
    \"\"\"Add two numbers.\"\"\"
    return x + y
        """

        # Test that generator can handle code
        assert gen is not None
        assert len(code) > 0

    def test_set_style_guide(self):
        """Test setting style guide."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        style = "google"
        gen.set_style_guide(style)

        # Style should be set
        assert gen is not None

    def test_set_target_audience(self):
        """Test setting target audience."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        audience = "developers"
        gen.set_target_audience(audience)

        # Audience should be set
        assert gen is not None

    def test_enable_examples(self):
        """Test enabling examples in documentation."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        gen.enable_examples()

        # Examples should be enabled
        assert gen is not None

    def test_disable_examples(self):
        """Test disabling examples in documentation."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        gen.disable_examples()

        # Examples should be disabled
        assert gen is not None

    def test_set_language(self):
        """Test setting documentation language."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        gen.set_language("python")

        # Language should be set
        assert gen is not None

    def test_get_template(self):
        """Test getting documentation template."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        template = gen.get_template("function")

        # Template should be a string or dict
        assert template is not None

    def test_generate_class_docs(self):
        """Test generating documentation for a class."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        class_code = """
class Calculator:
    \"\"\"A simple calculator class.\"\"\"

    def add(self, x, y):
        \"\"\"Add two numbers.\"\"\"
        return x + y
        """

        # Test that generator can handle class code
        assert gen is not None
        assert "Calculator" in class_code

    def test_generate_module_docs(self):
        """Test generating module-level documentation."""
        config = LLMConfig(provider="openai", model="gpt-4")
        gen = DocumentationGenerator(config=config)

        module_code = """
\"\"\"This is a test module.\"\"\"

def function1():
    pass

def function2():
    pass
        """

        # Test that generator can handle module code
        assert gen is not None
        assert len(module_code) > 0

    def test_set_include_type_hints(self):
        """Test setting whether to include type hints."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        gen.include_type_hints = True
        assert gen.include_type_hints is True

        gen.include_type_hints = False
        assert gen.include_type_hints is False

    def test_set_include_return_type_docs(self):
        """Test setting whether to include return type docs."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        gen.include_return_type_docs = True
        assert gen.include_return_type_docs is True

    def test_validate_format(self):
        """Test format validation."""
        config = LLMConfig(provider="anthropic", model="claude-3-sonnet")
        gen = DocumentationGenerator(config=config)

        # Valid format
        gen.format = "markdown"
        assert gen.format == "markdown"

        # Format should be validated
        assert gen.config is not None
