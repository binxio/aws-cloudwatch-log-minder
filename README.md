# AWS Cloudwatch Log minder
AWS CloudWatch logs is an useful logging system, but it has two quircks. It does not allow you too set a default
retention period for newly created log groups, and it does not delete empty log streams that are older than
the retention period. This utility:

1. sets a default retention period on log groups without a period set.
1. removes empty log streams older than the retention period of the log group

You can use it as a command line utility. You can also install it as an AWS Lambda function and have your
logs kept in order, NoOps style!

## install the log minder
to install the log minder, type:

```sh
pip install aws-cloudwatch-log-minder
```

## set default retention period
to set the default retention period on log groups without one, type:
```sh
cwlog-minder --dry-run set-log-retention --days 30
```
This will show you which log groups will have its retention period set. Remove the `--dry-run` and
it the retention period will be set. If you wish to set the retention of all log groups to the same
value, type:
```sh
cwlog-minder --dry-run set-log-retention --days 30 --overwrite
```

## delete empty log streams
To delete empty log streams older than the retention period, type:
```sh
cwlog-minder --dry-run delete-empty-log-streams
```
This will show you which empty log streams will be deleted. Remove the `--dry-run` and
these stream will be deleted.


## deploy the log minder
To deploy the log minder as an AWS Lambda, type:

```sh
git clone https://github.com/binxio/aws-cloudwatch-log-minder.git
cd aws-cloudwatch-log-minder
aws cloudformation deploy \
	--capabilities CAPABILITY_IAM \
	--stack-name aws-cloudwatch-log-minder \
	--template-file ./cloudformation/aws-cloudwatch-log-minder.yaml \
	--parameter-overrides LogRetentionInDays=30
```
This will install the log minder in your AWS account and run every hour.

## delete empty log groups
To delete empty log groups, type:
```sh
cwlog-minder --dry-run delete-empty-log-groups
```
This will show you which empty log groups will be deleted. Remove the `--dry-run` and
these groups will be deleted. Do not use this command, if your log groups are
managed by CloudFormation or Terraform.

## verbose

```sh
export LOG_LEVEL=INFO
cwlog-minder ...
```

## region and profile selection
AWS regions and credential profiles can be selected via command line
arguments or environment variables.

### region via parameter
```sh
cwlog-minder --region eu-west-1 ...
```

### region via environment
```sh
export AWS_DEFAULT_REGION=eu-west-1
cwlog-minder ...
```

### profile via parameter
```sh
cwlog-minder --profile dev ...
```

### profile via environment

```sh
export AWS_PROFILE=dev
cwlog-minder ...
```
