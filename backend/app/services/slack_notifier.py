import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)


def send_slack_alert(dataset_name, changes):

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL is not configured.")
        return

    high_severity_changes = [
        change
        for change in changes
        if change["severity"] == "HIGH"
    ]

    if not high_severity_changes:
        return

    message_lines = [
        "🚨 *HIGH Schema Drift Detected*",
        "",
        f"*Dataset:* {dataset_name}",
    ]

    for change in high_severity_changes:

        message_lines.extend([
            "",
            f"*Column:* {change['column']}",
            f"*Change:* {change['change_type']}",
            f"*Old:* {change.get('old_value')}",
            f"*New:* {change.get('new_value')}",
            f"*Severity:* {change['severity']}",
        ])

    payload = {
        "text": "\n".join(message_lines)
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException:
        logger.exception(
            "Failed to send Slack alert for dataset '%s'.",
            dataset_name
        )