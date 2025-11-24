"""
Monitoring and metrics utilities for the cocobot application.

This module provides comprehensive monitoring, metrics collection,
and health check functionality for the bot.
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import threading
from collections import defaultdict, deque
from contextlib import contextmanager
import json
from pathlib import Path


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str]
    timestamp: datetime


class MetricsCollector:
    """Collects and stores application metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._lock = threading.Lock()
        self.start_time = datetime.utcnow()
        self.logger = logging.getLogger(__name__)
    
    def add_metric(self, name: str, metric_type: MetricType, value: float, labels: Dict[str, str] = None):
        """Add a metric to the collector."""
        if labels is None:
            labels = {}
        
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            labels=labels,
            timestamp=datetime.utcnow()
        )
        
        with self._lock:
            self.metrics[name].append(metric)
    
    def increment_counter(self, name: str, labels: Dict[str, str] = None, amount: float = 1.0):
        """Increment a counter metric."""
        self.add_metric(name, MetricType.COUNTER, amount, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value."""
        self.add_metric(name, MetricType.GAUGE, value, labels)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram observation."""
        self.add_metric(name, MetricType.HISTOGRAM, value, labels)
    
    def get_metric(self, name: str) -> List[Metric]:
        """Get all values for a specific metric."""
        with self._lock:
            return self.metrics.get(name, []).copy()
    
    def get_latest_value(self, name: str) -> Optional[float]:
        """Get the latest value for a specific metric."""
        with self._lock:
            metrics = self.metrics.get(name, [])
            if metrics:
                return metrics[-1].value
        return None
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        with self._lock:
            summary = {}
            for name, metrics in self.metrics.items():
                if metrics:
                    values = [m.value for m in metrics]
                    summary[name] = {
                        'count': len(values),
                        'latest': values[-1],
                        'average': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values)
                    }
            return summary
    
    def clear_metrics(self, name: str = None):
        """Clear metrics, either all or for a specific name."""
        with self._lock:
            if name:
                if name in self.metrics:
                    del self.metrics[name]
            else:
                self.metrics.clear()


class HealthChecker:
    """Health check functionality for the bot."""
    
    def __init__(self):
        self.checks: Dict[str, Callable[[], bool]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_check(self, name: str, check_func: Callable[[], bool]):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def add_database_check(self, db_session_getter):
        """Add a database connectivity check."""
        def check_db():
            try:
                # Try to get a database session and run a simple query
                with db_session_getter() as db:
                    # Run a simple query to test connectivity
                    db.execute("SELECT 1")
                    return True
            except Exception as e:
                self.logger.error(f"Database health check failed: {e}")
                return False
        
        self.register_check("database", check_db)
    
    def add_api_check(self, name: str, test_func: Callable[[], bool]):
        """Add an API connectivity check."""
        self.register_check(f"api_{name}", test_func)
    
    def check_all(self) -> Dict[str, bool]:
        """Run all registered health checks."""
        results = {}
        for name, check_func in self.checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                self.logger.error(f"Health check '{name}' failed with error: {e}")
                results[name] = False
        return results
    
    def is_healthy(self) -> bool:
        """Check if all health checks pass."""
        results = self.check_all()
        return all(results.values()) if results else True


class PerformanceMonitor:
    """Monitors application performance and resource usage."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.start_time = datetime.utcnow()
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get system resource metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'process_memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
            'process_cpu_percent': psutil.Process().cpu_percent()
        }
    
    def collect_system_metrics(self):
        """Collect and store system metrics."""
        metrics = self.get_system_metrics()
        for name, value in metrics.items():
            self.metrics_collector.set_gauge(f"system_{name}", value)
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    def get_uptime_metrics(self) -> Dict[str, float]:
        """Get uptime-related metrics."""
        uptime = self.get_uptime()
        return {
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'start_time': self.start_time.timestamp()
        }
    
    @contextmanager
    def time_execution(self, metric_name: str, labels: Dict[str, str] = None):
        """Context manager to time execution of a block and record it as a metric."""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self.metrics_collector.observe_histogram(metric_name, execution_time, labels)
            self.logger.debug(f"{metric_name} executed in {execution_time:.3f}s")
    
    def time_function(self, metric_name: str = None):
        """Decorator to time function execution."""
        def decorator(func):
            nonlocal metric_name
            if metric_name is None:
                metric_name = f"function_{func.__name__}_duration"
            
            def wrapper(*args, **kwargs):
                with self.time_execution(metric_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


class BotMetrics:
    """High-level metrics for the bot application."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        self.logger = logging.getLogger(__name__)
    
    def increment_command_usage(self, command_name: str, success: bool = True):
        """Increment command usage counter."""
        labels = {'command': command_name, 'success': str(success)}
        self.performance_monitor.metrics_collector.increment_counter(
            "command_executions_total", labels
        )
    
    def record_command_duration(self, command_name: str, duration_seconds: float, success: bool = True):
        """Record command execution duration."""
        labels = {'command': command_name, 'success': str(success)}
        self.performance_monitor.metrics_collector.observe_histogram(
            "command_duration_seconds", duration_seconds, labels
        )
    
    def increment_api_call(self, api_name: str, success: bool = True):
        """Increment API call counter."""
        labels = {'api': api_name, 'success': str(success)}
        self.performance_monitor.metrics_collector.increment_counter(
            "api_calls_total", labels
        )
    
    def record_api_duration(self, api_name: str, duration_seconds: float, success: bool = True):
        """Record API call duration."""
        labels = {'api': api_name, 'success': str(success)}
        self.performance_monitor.metrics_collector.observe_histogram(
            "api_duration_seconds", duration_seconds, labels
        )
    
    def increment_error(self, error_type: str, error_message: str = None):
        """Increment error counter."""
        labels = {'type': error_type}
        if error_message:
            labels['message'] = error_message[:100]  # Truncate long messages
        self.performance_monitor.metrics_collector.increment_counter(
            "errors_total", labels
        )
    
    def record_user_interaction(self, interaction_type: str, user_id: str):
        """Record user interaction."""
        labels = {'type': interaction_type, 'user_id': str(user_id)}
        self.performance_monitor.metrics_collector.increment_counter(
            "user_interactions_total", labels
        )
    
    def get_command_stats(self) -> Dict[str, Any]:
        """Get command execution statistics."""
        command_metrics = self.performance_monitor.metrics_collector.get_metric("command_executions_total")
        stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failure': 0})
        
        for metric in command_metrics:
            cmd = metric.labels.get('command', 'unknown')
            success = metric.labels.get('success', 'true') == 'true'
            
            stats[cmd]['total'] += metric.value
            if success:
                stats[cmd]['success'] += metric.value
            else:
                stats[cmd]['failure'] += metric.value
        
        return dict(stats)
    
    def export_metrics(self) -> str:
        """Export metrics in a standard format (like Prometheus text format)."""
        output = []
        # Add system metrics
        system_metrics = self.performance_monitor.get_system_metrics()
        for name, value in system_metrics.items():
            output.append(f"system_{name} {value}")
        
        # Add uptime metrics
        uptime_metrics = self.performance_monitor.get_uptime_metrics()
        for name, value in uptime_metrics.items():
            output.append(f"bot_{name} {value}")
        
        # Add custom metrics
        for metric_name, metrics in self.performance_monitor.metrics_collector.metrics.items():
            if metrics:
                latest = metrics[-1]
                labels_str = ",".join([f'{k}="{v}"' for k, v in latest.labels.items()])
                if labels_str:
                    output.append(f'{metric_name}{{{labels_str}}} {latest.value}')
                else:
                    output.append(f'{metric_name} {latest.value}')
        
        return "\n".join(output)
    
    def save_metrics_to_file(self, filepath: str = None):
        """Save metrics to a JSON file."""
        if filepath is None:
            # Create metrics directory if it doesn't exist
            metrics_dir = Path("metrics")
            metrics_dir.mkdir(exist_ok=True)
            filepath = metrics_dir / f"metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        metrics_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'system_metrics': self.performance_monitor.get_system_metrics(),
            'uptime': self.performance_monitor.get_uptime(),
            'custom_metrics': dict(self.performance_monitor.metrics_collector.metrics)
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, default=str, indent=2)
        
        self.logger.info(f"Metrics saved to {filepath}")


# Global instances
_metrics_instance = None
_health_checker_instance = None


def get_bot_metrics() -> BotMetrics:
    """Get the global bot metrics instance."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = BotMetrics()
    return _metrics_instance


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker_instance
    if _health_checker_instance is None:
        _health_checker_instance = HealthChecker()
    return _health_checker_instance


# Convenience functions
def increment_command_usage(command_name: str, success: bool = True):
    """Increment command usage counter."""
    get_bot_metrics().increment_command_usage(command_name, success)


def record_command_duration(command_name: str, duration_seconds: float, success: bool = True):
    """Record command execution duration."""
    get_bot_metrics().record_command_duration(command_name, duration_seconds, success)


def increment_api_call(api_name: str, success: bool = True):
    """Increment API call counter."""
    get_bot_metrics().increment_api_call(api_name, success)


def record_api_duration(api_name: str, duration_seconds: float, success: bool = True):
    """Record API call duration."""
    get_bot_metrics().record_api_duration(api_name, duration_seconds, success)


def increment_error(error_type: str, error_message: str = None):
    """Increment error counter."""
    get_bot_metrics().increment_error(error_type, error_message)


def time_command(command_name: str):
    """Decorator to time command execution and record metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                record_command_duration(command_name, duration, success)
                increment_command_usage(command_name, success)
        return wrapper
    return decorator


def time_api_call(api_name: str):
    """Decorator to time API calls and record metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                record_api_duration(api_name, duration, success)
                increment_api_call(api_name, success)
        return wrapper
    return decorator


# Initialize metrics at module level
bot_metrics = get_bot_metrics()
health_checker = get_health_checker()