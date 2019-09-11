# AWS Cloudwatch Log minder
the AWS Cloudwatch Log minder, has two tasks:
- remove empty log streams older than the retention period of the log group
- set a default retention period on log groups without a period set.

## deploy the log minder
To deploy the log minder, type:

```sh
git clone https://github.com/binxio/aws-cloudwatch-log-minder.git
cd aws-cloudwatch-log-minder
aws cloudformation create-stack \
        --capabilities CAPABILITY_IAM \
        --stack-name aws-cloudwatch-log-minder \
        --template-body file://./cloudformation/aws-cloudwatch-log-minder.yaml

aws cloudformation wait stack-create-complete  --stack-name aws-cloudwatch-log-minder
```

It is scheduled to run every day around midnight.

You can also use the command line utility:

```sh
pip install aws-cloudwatch-log-minder
```
