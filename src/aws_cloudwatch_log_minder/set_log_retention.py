import os
import boto3
from botocore.exceptions import ClientError
from .logger import log


cw_logs = None


def set_log_retention(
    log_group_name_prefix: str = None,
    retention_in_days: int = 30,
    overwrite: bool = False,
    dry_run: bool = False,
    region: str = None,
    profile: str = None,
):
    global cw_logs

    boto_session = boto3.Session(region_name=region, profile_name=profile)
    cw_logs = boto_session.client("logs")

    kwargs = {"PaginationConfig": {"PageSize": 50}}
    if log_group_name_prefix:
        kwargs["logGroupNamePrefix"] = log_group_name_prefix
        log.info("finding log groups with prefix %r", log_group_name_prefix)

    for response in cw_logs.get_paginator("describe_log_groups").paginate(**kwargs):
        for group in response["logGroups"]:
            log_group_name = group["logGroupName"]
            current_retention = group.get("retentionInDays")
            if not current_retention or (
                overwrite and int(current_retention) != retention_in_days
            ):
                try:
                    if current_retention:
                        log.info(
                            "%s overwriting current retention period of %s of log stream %s to %s",
                            ("dry run" if dry_run else ""),
                            current_retention,
                            log_group_name,
                            retention_in_days,
                        )
                    else:
                        log.info(
                            "%s setting default retention period of log stream %s to %s",
                            ("dry run" if dry_run else ""),
                            log_group_name,
                            retention_in_days,
                        )
                    if dry_run:
                        continue
                    cw_logs.put_retention_policy(
                        logGroupName=log_group_name, retentionInDays=retention_in_days
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
    global cw_logs

    cw_logs = boto3.client("logs")

    dry_run = request.get("dry_run", False)
    if "dry_run" in request and not isinstance(dry_run, bool):
        raise ValueError(f"'dry_run' is not a boolean value, {request}")

    overwrite = request.get("overwrite", False)
    if "overwrite" in request and not isinstance(overwrite, bool):
        raise ValueError(f"'overwrite' is not a boolean value, {request}")

    default_log_retention = int(os.getenv("DEFAULT_LOG_RETENTION_IN_DAYS", "30"))
    days = request.get("days", default_log_retention)
    if "days" in request and not isinstance(days, int):
        raise ValueError(f"'days' is not a integer value, {request}")

    log_group_name_prefix = request.get("log_group_name_prefix")

    set_log_retention(
        log_group_name_prefix=log_group_name_prefix,
        retention_in_days=days,
        overwrite=overwrite,
        dry_run=dry_run,
    )
