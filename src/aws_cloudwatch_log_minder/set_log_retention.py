import os
import boto3
from botocore.exceptions import ClientError
from .logger import log

cw_logs = boto3.client("logs")


def set_log_retention(retention_in_days: int = 30, dry_run: bool = False):
    for response in cw_logs.get_paginator("describe_log_groups").paginate():
        for group in response["logGroups"]:
            log_group_name = group["logGroupName"]
            current_retention = group.get("retentionInDays")
            if not current_retention  or int(current_retention) > retention_in_days:
                try:
                    log.info(
                        "setting default retention period of log stream %s to %s",
                        log_group_name,
                        retention_in_days,
                    )
                    if dry_run:
                        continue
                    cw_logs.put_retention_policy(
                        logGroupName=log_group_name,
                        retentionInDays=retention_in_days,
                    )
                except ClientError as e:
                    log.error(
                        "failed to set retention period of log stream %s to %s, %s",
                        log_group_name,
                        retention_in_days,
                        e,
                    )
            else:
                log.debug(
                    "retention period on %s already set to %s",
                    log_group_name,
                    current_retention,
                )


def handle(request, context):
    dry_run = request.get("dry_run", False)
    if "dry_run" in request and not isinstance(dry_run, bool):
        raise ValueError(f"'dry_run' is not a boolean value, {request}")

    default_log_retention = int(os.getenv("DEFAULT_LOG_RETENTION_IN_DAYS", "30"))
    days = request.get("days", default_log_retention)
    if "days" in request and not isinstance(days, int):
        raise ValueError(f"'days' is not a integer value, {request}")

    set_log_retention(days, dry_run)
