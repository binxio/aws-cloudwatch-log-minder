import os
import boto3
from botocore.exceptions import ClientError
from .logging import log

cw_logs = boto3.client('logs')

def set_log_retention(default_retention_period:int = 30, dry_run: bool = False):
    for response in cw_logs.get_paginator('describe_log_groups').paginate():
        for group in response['logGroups']:
            log_group_name = group["logGroupName"]
            current_retention = group.get('retentionInDays')
            if not current_retention:
                try:
                    log.info('setting default retention period of log stream %s to %s', log_group_name, default_retention_period)
                    if dry_run:
                        continue
                    cw_logs.put_retention_policy(
                        logGroupName=log_group_name,
                        retentionInDays=default_retention_period
                    )
                except ClientError as e:
                    log.error('failed to set retention period of log stream %s to %s, %s', log_group_name, default_retention_period, e)
            else:
                log.debug('retention period on %s already set to %s', log_group_name, current_retention)


def handle(request={}, context={}):
    log.info('setting default retention period on newly created log groups')
    default_retention_period = int(os.getenv('DEFAULT_RETENTION_PERIOD_IN_DAYS', '30'))
    set_log_retention(default_retention_period)


