import os
import boto3
from botocore.exceptions import ClientError
from .logging import log
from datetime import datetime

cw_logs = boto3.client('logs')


def _delete_empty_log_streams(group: dict, oldest_in_ms: int, dry_run: bool):
    log_group_name = group["logGroupName"]
    kwargs = {
        "logGroupName": log_group_name,
        "orderBy": 'LastEventTime',
        "descending": False
    }
    for response in cw_logs.get_paginator('describe_log_streams').paginate(**kwargs):
        for stream in response['logStreams']:
            log_stream_name = stream['logStreamName']
            if stream["creationTime"] > oldest_in_ms:
                log.debug('keeping log stream %s from group %s as it is within retention period', log_stream_name, log_group_name)
                continue

            if not stream["storedBytes"] == 0 and stream["creationTime"] < oldest_in_ms:
                try:
                    log.info('deleting log stream %s from group %s', log_stream_name, log_group_name)
                    if dry_run:
                        continue
                    cw_logs.delete_log_stream(
                        logGroupName=log_group_name,
                        logStreamName=log_stream_name
                    )
                except ClientError as e:
                    log.error('failed to delete log stream %s from group %s, %s', log_stream_name, log_group_name, e)
            else:
                log.debug('keeping log stream %s from group %s', log_stream_name, log_group_name)

def delete_empty_log_streams(dry_run: bool = False):
    log.info('cleaning empty log streams older than the retention period of the group')
    now = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    for response in cw_logs.get_paginator('describe_log_groups').paginate():
        for group in response['logGroups']:
            oldest = now - (group.get('retentionInDays', 365) * 24 * 3600)
            _delete_empty_log_streams(group, oldest * 1000, dry_run)


def handle(request, context):
    delete_empty_log_streams()
