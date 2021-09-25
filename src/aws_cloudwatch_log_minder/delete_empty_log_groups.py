import json
from datetime import datetime, timedelta
from typing import List

import boto3
from botocore.config import Config

from .logger import log

cw_logs = None


def delete_empty_log_groups(
    log_group_name_prefix: str = None,
    dry_run: bool = False,
    region: str = None,
    profile: str = None,
):
    global cw_logs

    boto_session = boto3.Session(region_name=region, profile_name=profile)
    cw_logs = boto_session.client("logs", config=Config(retries=dict(max_attempts=10)))

    kwargs = {"PaginationConfig": {"PageSize": 50}}
    if log_group_name_prefix:
        kwargs["logGroupNamePrefix"] = log_group_name_prefix
        log.info("finding log groups with prefix %r", log_group_name_prefix)

    for response in cw_logs.get_paginator("describe_log_groups").paginate(**kwargs):
        for group in response["logGroups"]:
            log_group_name = group["logGroupName"]
            response = cw_logs.describe_log_streams(logGroupName=log_group_name)
            if len(response["logStreams"]) == 0:
                log.info(
                    "%s deleting empty log group %s",
                    ("dry run" if dry_run else ""),
                    log_group_name,
                )
                if dry_run:
                    continue
                cw_logs.delete_log_group(logGroupName=log_group_name)
            else:
                log.info(
                    "%s keeping log group %s as it is not empty",
                    ("dry run" if dry_run else ""),
                    log_group_name,
                )


def get_all_log_group_names() -> List[str]:
    result: List[str] = []
    for response in cw_logs.get_paginator("describe_log_groups").paginate(
        PaginationConfig={"PageSize": 50}
    ):
        result.extend(list(map(lambda g: g["logGroupName"], response["logGroups"])))
    return result


def fan_out(function_arn: str, log_group_names: List[str], dry_run: bool):
    awslambda = boto3.client("lambda")
    log.info(
        "recursively invoking %s to delete empty groups from %d log groups",
        function_arn,
        len(log_group_names),
    )
    for log_group_name in log_group_names:
        payload = json.dumps(
            {
                "log_group_name_prefix": log_group_name,
                "dry_run": dry_run,
            }
        )
        awslambda.invoke(
            FunctionName=function_arn, InvocationType="Event", Payload=payload
        )


def handle(request, context):
    global cw_logs

    cw_logs = boto3.client("logs", config=Config(retries=dict(max_attempts=10)))

    dry_run = request.get("dry_run", False)
    if "dry_run" in request and not isinstance(dry_run, bool):
        raise ValueError(f"'dry_run' is not a boolean value, {request}")

    log_group_name_prefix = request.get("log_group_name_prefix")
    if log_group_name_prefix:
        delete_empty_log_groups(log_group_name_prefix, dry_run)
    else:
        fan_out(
            context.invoked_function_arn,
            get_all_log_group_names(),
            dry_run,
        )
