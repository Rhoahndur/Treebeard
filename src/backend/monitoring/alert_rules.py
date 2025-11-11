"""
Alert Rules and Notification Management.

This module defines alert rules and manages notifications through various channels:
- PagerDuty for critical alerts
- Slack for warnings and notifications
- Email for digests

Alert Severity Levels:
- Critical: Production-impacting issues requiring immediate attention
- High: Important issues that need prompt response
- Medium: Issues that should be investigated
- Low: Informational alerts
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class NotificationChannel(str, Enum):
    """Notification channels."""

    PAGERDUTY = "pagerduty"
    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"


@dataclass
class AlertRule:
    """
    Alert rule definition.

    Attributes:
        name: Alert rule name
        description: Alert description
        condition: Alert condition expression
        severity: Alert severity level
        channels: Notification channels
        threshold: Alert threshold value
        duration: Duration condition must be true (in seconds)
        enabled: Whether the alert is enabled
        runbook_url: URL to incident runbook
        tags: Additional tags for grouping
    """

    name: str
    description: str
    condition: str
    severity: AlertSeverity
    channels: List[NotificationChannel]
    threshold: float
    duration: int
    enabled: bool = True
    runbook_url: Optional[str] = None
    tags: Optional[List[str]] = None


# Critical Alerts - PagerDuty
CRITICAL_ALERTS = [
    AlertRule(
        name="high_error_rate",
        description="API error rate exceeded threshold",
        condition="error_rate > 5%",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=5.0,
        duration=300,  # 5 minutes
        runbook_url="/docs/runbooks/high-error-rate.md",
        tags=["api", "errors"],
    ),
    AlertRule(
        name="high_api_latency",
        description="API P95 latency exceeded threshold",
        condition="api_latency_p95 > 3s",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=3000.0,  # 3 seconds in milliseconds
        duration=600,  # 10 minutes
        runbook_url="/docs/runbooks/high-latency.md",
        tags=["api", "performance"],
    ),
    AlertRule(
        name="database_connection_failure",
        description="Database connections failing",
        condition="database_errors > 0",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=1.0,
        duration=60,  # 1 minute
        runbook_url="/docs/runbooks/database-issues.md",
        tags=["database", "infrastructure"],
    ),
    AlertRule(
        name="redis_unavailable",
        description="Redis cache unavailable",
        condition="redis_connection_errors > 0",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=1.0,
        duration=60,  # 1 minute
        runbook_url="/docs/runbooks/cache-failure.md",
        tags=["cache", "infrastructure"],
    ),
    AlertRule(
        name="claude_api_rate_limit",
        description="Claude API rate limit exceeded",
        condition="claude_api_rate_limit_errors > 0",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=1.0,
        duration=60,  # 1 minute
        runbook_url="/docs/runbooks/claude-api-issues.md",
        tags=["external_api", "claude"],
    ),
    AlertRule(
        name="high_cpu_usage",
        description="CPU usage critically high",
        condition="cpu_usage > 90%",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=90.0,
        duration=900,  # 15 minutes
        runbook_url="/docs/runbooks/high-resource-usage.md",
        tags=["infrastructure", "cpu"],
    ),
    AlertRule(
        name="high_memory_usage",
        description="Memory usage critically high",
        condition="memory_usage > 85%",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=85.0,
        duration=300,  # 5 minutes
        runbook_url="/docs/runbooks/high-resource-usage.md",
        tags=["infrastructure", "memory"],
    ),
    AlertRule(
        name="low_disk_space",
        description="Disk space critically low",
        condition="disk_usage > 90%",
        severity=AlertSeverity.CRITICAL,
        channels=[NotificationChannel.PAGERDUTY, NotificationChannel.SLACK],
        threshold=90.0,
        duration=300,  # 5 minutes
        runbook_url="/docs/runbooks/disk-space.md",
        tags=["infrastructure", "disk"],
    ),
]

# Warning Alerts - Slack
WARNING_ALERTS = [
    AlertRule(
        name="elevated_error_rate",
        description="API error rate elevated",
        condition="error_rate > 2%",
        severity=AlertSeverity.HIGH,
        channels=[NotificationChannel.SLACK],
        threshold=2.0,
        duration=600,  # 10 minutes
        runbook_url="/docs/runbooks/high-error-rate.md",
        tags=["api", "errors"],
    ),
    AlertRule(
        name="elevated_api_latency",
        description="API P95 latency elevated",
        condition="api_latency_p95 > 2s",
        severity=AlertSeverity.HIGH,
        channels=[NotificationChannel.SLACK],
        threshold=2000.0,  # 2 seconds in milliseconds
        duration=900,  # 15 minutes
        runbook_url="/docs/runbooks/high-latency.md",
        tags=["api", "performance"],
    ),
    AlertRule(
        name="low_cache_hit_rate",
        description="Cache hit rate below target",
        condition="cache_hit_rate < 60%",
        severity=AlertSeverity.MEDIUM,
        channels=[NotificationChannel.SLACK],
        threshold=60.0,
        duration=1800,  # 30 minutes
        runbook_url="/docs/runbooks/cache-performance.md",
        tags=["cache", "performance"],
    ),
    AlertRule(
        name="slow_database_queries",
        description="Slow database queries detected",
        condition="slow_query_count > 10",
        severity=AlertSeverity.MEDIUM,
        channels=[NotificationChannel.SLACK],
        threshold=10.0,
        duration=600,  # 10 minutes
        runbook_url="/docs/runbooks/database-issues.md",
        tags=["database", "performance"],
    ),
    AlertRule(
        name="high_recommendation_time",
        description="Recommendation generation time high",
        condition="recommendation_duration_p95 > 5s",
        severity=AlertSeverity.MEDIUM,
        channels=[NotificationChannel.SLACK],
        threshold=5000.0,  # 5 seconds in milliseconds
        duration=900,  # 15 minutes
        runbook_url="/docs/runbooks/slow-recommendations.md",
        tags=["recommendation", "performance"],
    ),
    AlertRule(
        name="claude_api_errors",
        description="Claude API errors detected",
        condition="claude_api_error_rate > 5%",
        severity=AlertSeverity.HIGH,
        channels=[NotificationChannel.SLACK],
        threshold=5.0,
        duration=300,  # 5 minutes
        runbook_url="/docs/runbooks/claude-api-issues.md",
        tags=["external_api", "claude"],
    ),
    AlertRule(
        name="elevated_cpu_usage",
        description="CPU usage elevated",
        condition="cpu_usage > 75%",
        severity=AlertSeverity.MEDIUM,
        channels=[NotificationChannel.SLACK],
        threshold=75.0,
        duration=1800,  # 30 minutes
        runbook_url="/docs/runbooks/high-resource-usage.md",
        tags=["infrastructure", "cpu"],
    ),
    AlertRule(
        name="elevated_memory_usage",
        description="Memory usage elevated",
        condition="memory_usage > 70%",
        severity=AlertSeverity.MEDIUM,
        channels=[NotificationChannel.SLACK],
        threshold=70.0,
        duration=1800,  # 30 minutes
        runbook_url="/docs/runbooks/high-resource-usage.md",
        tags=["infrastructure", "memory"],
    ),
]

# Informational Alerts - Email digest
INFO_ALERTS = [
    AlertRule(
        name="daily_error_summary",
        description="Daily error summary",
        condition="daily",
        severity=AlertSeverity.INFO,
        channels=[NotificationChannel.EMAIL],
        threshold=0.0,
        duration=86400,  # Daily
        tags=["summary", "errors"],
    ),
    AlertRule(
        name="weekly_performance_report",
        description="Weekly performance report",
        condition="weekly",
        severity=AlertSeverity.INFO,
        channels=[NotificationChannel.EMAIL],
        threshold=0.0,
        duration=604800,  # Weekly
        tags=["summary", "performance"],
    ),
]

# All alert rules
ALL_ALERT_RULES = CRITICAL_ALERTS + WARNING_ALERTS + INFO_ALERTS


def get_alert_rules(severity: Optional[AlertSeverity] = None, enabled_only: bool = True) -> List[AlertRule]:
    """
    Get alert rules filtered by severity and enabled status.

    Args:
        severity: Filter by severity level
        enabled_only: Only return enabled rules

    Returns:
        List of alert rules
    """
    rules = ALL_ALERT_RULES

    if enabled_only:
        rules = [rule for rule in rules if rule.enabled]

    if severity:
        rules = [rule for rule in rules if rule.severity == severity]

    return rules


def get_alert_rule(name: str) -> Optional[AlertRule]:
    """
    Get a specific alert rule by name.

    Args:
        name: Alert rule name

    Returns:
        Alert rule or None if not found
    """
    for rule in ALL_ALERT_RULES:
        if rule.name == name:
            return rule
    return None


def evaluate_alert_condition(rule: AlertRule, current_value: float) -> bool:
    """
    Evaluate if an alert condition is met.

    Args:
        rule: Alert rule to evaluate
        current_value: Current metric value

    Returns:
        True if alert should fire, False otherwise
    """
    # Simple threshold comparison
    # In production, this would be handled by the monitoring platform
    return current_value > rule.threshold


def format_alert_message(rule: AlertRule, current_value: float, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Format an alert message for notification.

    Args:
        rule: Alert rule that fired
        current_value: Current value that triggered the alert
        context: Additional context

    Returns:
        Formatted alert message
    """
    message = f"""
🚨 **{rule.severity.upper()} ALERT**: {rule.name}

**Description**: {rule.description}

**Condition**: {rule.condition}
**Current Value**: {current_value}
**Threshold**: {rule.threshold}

**Severity**: {rule.severity}
**Tags**: {', '.join(rule.tags or [])}
"""

    if rule.runbook_url:
        message += f"\n**Runbook**: {rule.runbook_url}"

    if context:
        message += "\n\n**Additional Context**:\n"
        for key, value in context.items():
            message += f"- {key}: {value}\n"

    return message.strip()


def send_alert(
    rule: AlertRule,
    current_value: float,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Send an alert through configured channels.

    Args:
        rule: Alert rule that fired
        current_value: Current value that triggered the alert
        context: Additional context
    """
    message = format_alert_message(rule, current_value, context)

    for channel in rule.channels:
        try:
            if channel == NotificationChannel.PAGERDUTY:
                _send_pagerduty_alert(rule, message, context)
            elif channel == NotificationChannel.SLACK:
                _send_slack_alert(rule, message, context)
            elif channel == NotificationChannel.EMAIL:
                _send_email_alert(rule, message, context)
            elif channel == NotificationChannel.WEBHOOK:
                _send_webhook_alert(rule, message, context)
        except Exception as e:
            logger.error(f"Failed to send alert via {channel}: {e}")


def _send_pagerduty_alert(rule: AlertRule, message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Send alert to PagerDuty."""
    logger.info(f"[PagerDuty] {rule.name}: {message}")
    # Implementation would use PagerDuty API
    # import pypd
    # pypd.EventV2.create(
    #     data={
    #         'routing_key': PAGERDUTY_KEY,
    #         'event_action': 'trigger',
    #         'payload': {
    #             'summary': rule.description,
    #             'severity': rule.severity,
    #             'source': 'treebeard-api',
    #             'custom_details': context or {}
    #         }
    #     }
    # )


def _send_slack_alert(rule: AlertRule, message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Send alert to Slack."""
    logger.info(f"[Slack] {rule.name}: {message}")
    # Implementation would use Slack API
    # from slack_sdk import WebClient
    # client = WebClient(token=SLACK_TOKEN)
    # channel = '#alerts' if rule.severity == AlertSeverity.CRITICAL else '#warnings'
    # client.chat_postMessage(channel=channel, text=message)


def _send_email_alert(rule: AlertRule, message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Send alert via email."""
    logger.info(f"[Email] {rule.name}: {message}")
    # Implementation would use email service (SendGrid, SES, etc.)


def _send_webhook_alert(rule: AlertRule, message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """Send alert to webhook."""
    logger.info(f"[Webhook] {rule.name}: {message}")
    # Implementation would POST to configured webhook URL
