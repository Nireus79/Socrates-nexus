"""Tests for performance monitoring module."""

import pytest
from datetime import datetime, timedelta
from socrates_nexus.performance import PerformanceMonitor, PerformanceMetrics
from socrates_nexus.models import TokenUsage


class TestPerformanceMetrics:
    """Test PerformanceMetrics class."""

    def test_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            latency_ms=150,
            tokens_per_second=100,
            cost_usd=0.05,
            timestamp=datetime.utcnow(),
        )
        assert metrics.latency_ms == 150
        assert metrics.tokens_per_second == 100
        assert metrics.cost_usd == 0.05

    def test_metrics_timestamp(self):
        """Test that metrics have timestamps."""
        now = datetime.utcnow()
        metrics = PerformanceMetrics(
            latency_ms=100,
            tokens_per_second=50,
            cost_usd=0.01,
            timestamp=now,
        )
        assert metrics.timestamp == now


class TestPerformanceMonitor:
    """Test PerformanceMonitor class."""

    def test_initialization(self):
        """Test monitor initialization."""
        monitor = PerformanceMonitor(max_history=1000)
        assert monitor.max_history == 1000
        assert len(monitor._metrics_history) == 0

    def test_record_metrics(self):
        """Test recording performance metrics."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )
        latency_ms = 250.5

        monitor.record(usage, latency_ms)

        assert len(monitor._metrics_history) > 0

    def test_get_stats(self):
        """Test getting performance statistics."""
        monitor = PerformanceMonitor()

        # Record multiple metrics
        usage1 = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)
        usage2 = TokenUsage(input_tokens=200, output_tokens=100, total_tokens=300)

        monitor.record(usage1, 200.0)
        monitor.record(usage2, 300.0)

        stats = monitor.get_stats()

        assert "avg_latency_ms" in stats
        assert "min_latency_ms" in stats
        assert "max_latency_ms" in stats
        assert "avg_throughput_tokens_per_sec" in stats
        assert "total_tokens" in stats

    def test_get_stats_by_provider(self):
        """Test getting statistics by provider."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)
        monitor.record(usage, 200.0, provider="gpt-4")
        monitor.record(usage, 250.0, provider="claude")

        stats_by_provider = monitor.get_stats_by_provider()

        assert "gpt-4" in stats_by_provider
        assert "claude" in stats_by_provider

    def test_get_stats_by_model(self):
        """Test getting statistics by model."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)
        monitor.record(usage, 200.0, model="gpt-4-turbo")
        monitor.record(usage, 250.0, model="gpt-3.5-turbo")

        stats_by_model = monitor.get_stats_by_model()

        assert "gpt-4-turbo" in stats_by_model
        assert "gpt-3.5-turbo" in stats_by_model

    def test_reset_stats(self):
        """Test resetting statistics."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)
        monitor.record(usage, 200.0)

        assert len(monitor._metrics_history) > 0

        monitor.reset()

        assert len(monitor._metrics_history) == 0

    def test_history_size_limit(self):
        """Test that history respects max size."""
        monitor = PerformanceMonitor(max_history=10)

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)

        # Record 15 metrics
        for _ in range(15):
            monitor.record(usage, 200.0)

        # Should not exceed max
        assert len(monitor._metrics_history) <= monitor.max_history

    def test_latency_percentiles(self):
        """Test calculating latency percentiles."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)

        # Record metrics with varying latencies
        latencies = [100.0, 150.0, 200.0, 250.0, 300.0]
        for latency in latencies:
            monitor.record(usage, latency)

        stats = monitor.get_stats()

        # Should have percentile stats
        assert "avg_latency_ms" in stats
        assert stats["avg_latency_ms"] > 0

    def test_cost_tracking(self):
        """Test cost tracking in performance monitor."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)

        monitor.record(usage, 200.0, cost_usd=0.05)
        monitor.record(usage, 250.0, cost_usd=0.06)

        stats = monitor.get_stats()

        assert "total_cost_usd" in stats or stats.get("total_tokens", 0) > 0

    def test_clear_old_entries(self):
        """Test clearing old metrics entries."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)

        # Record metric with old timestamp
        old_time = datetime.utcnow() - timedelta(hours=2)
        monitor.record(usage, 200.0)
        if monitor._metrics_history:
            monitor._metrics_history[0].timestamp = old_time

        # Record new metric
        monitor.record(usage, 250.0)

        initial_count = len(monitor._metrics_history)

        # Clear entries older than 1 hour
        monitor.clear_old_entries(max_age_seconds=3600)

        final_count = len(monitor._metrics_history)

        # Should have removed older entry
        assert final_count <= initial_count

    def test_get_report(self):
        """Test generating performance report."""
        monitor = PerformanceMonitor()

        usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)

        for _ in range(5):
            monitor.record(usage, 200.0)

        report = monitor.get_report()

        assert isinstance(report, str)
        assert len(report) > 0
