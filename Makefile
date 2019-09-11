include Makefile.mk

NAME=aws-cloudwatch-log-minder
AWS_REGION=eu-central-1
S3_BUCKET_PREFIX=binxio-public
S3_BUCKET=$(S3_BUCKET_PREFIX)-$(AWS_REGION)

ALL_REGIONS=$(shell printf "import boto3\nprint('\\\n'.join(map(lambda r: r['RegionName'], boto3.client('ec2').describe_regions()['Regions'])))\n" | python | grep -v '^$(AWS_REGION)$$')

help:
	@echo 'make                 - builds a zip file to target/.'
	@echo 'make release         - builds a zip file and deploys it to s3.'
	@echo 'make clean           - the workspace.'
	@echo 'make test            - execute the tests, requires a working AWS connection.'
	@echo 'make deploy	    - lambda to bucket $(S3_BUCKET)'
	@echo 'make deploy-all-regions - lambda to all regions with bucket prefix $(S3_BUCKET_PREFIX)'
	@echo 'make deploy-lambda - deploys the manager.'
	@echo 'make delete-lambda - deletes the manager.'
	@echo 'make demo            - deploys the provider and the demo cloudformation stack.'
	@echo 'make delete-demo     - deletes the demo cloudformation stack.'

deploy: target/$(NAME)-$(VERSION).zip
	aws s3 --region $(AWS_REGION) \
		cp --acl \
		public-read target/$(NAME)-$(VERSION).zip \
		s3://$(S3_BUCKET)/lambdas/$(NAME)-$(VERSION).zip 
	aws s3 --region $(AWS_REGION) \
		cp --acl public-read \
		s3://$(S3_BUCKET)/lambdas/$(NAME)-$(VERSION).zip \
		s3://$(S3_BUCKET)/lambdas/$(NAME)-latest.zip 

deploy-all-regions: deploy
	@for REGION in $(ALL_REGIONS); do \
		echo "copying to region $$REGION.." ; \
		aws s3 --region $$REGION \
			cp --acl public-read \
			s3://$(S3_BUCKET_PREFIX)-$(AWS_REGION)/lambdas/$(NAME)-$(VERSION).zip \
			s3://$(S3_BUCKET_PREFIX)-$$REGION/lambdas/$(NAME)-$(VERSION).zip; \
		aws s3 --region $$REGION \
			cp  --acl public-read \
			s3://$(S3_BUCKET_PREFIX)-$$REGION/lambdas/$(NAME)-$(VERSION).zip \
			s3://$(S3_BUCKET_PREFIX)-$$REGION/lambdas/$(NAME)-latest.zip; \
	done

do-push: deploy

do-build: target/$(NAME)-$(VERSION).zip

do-dist: target/$(NAME)-$(VERSION).zip
	rm -rf dist/*
	pipenv shell python setup.py sdist
	pipenv twine upload dist/*

target/$(NAME)-$(VERSION).zip: src/*/*.py requirements.txt Dockerfile.lambda
	mkdir -p target
	docker build --build-arg ZIPFILE=$(NAME)-$(VERSION).zip -t $(NAME)-lambda:$(VERSION) -f Dockerfile.lambda . && \
		ID=$$(docker create $(NAME)-lambda:$(VERSION) /bin/true) && \
		docker export $$ID | (cd target && tar -xvf - $(NAME)-$(VERSION).zip) && \
		docker rm -f $$ID && \
		chmod ugo+r target/$(NAME)-$(VERSION).zip

venv: requirements.txt
	virtualenv -p python3 venv  && \
	. ./venv/bin/activate && \
	pip install --quiet --upgrade pip && \
	pip install --quiet -r requirements.txt

clean:
	rm -rf venv target
	find . -name \*.pyc | xargs rm 

test: venv
	for i in $$PWD/cloudformation/*; do \
		aws cloudformation validate-template --template-body file://$$i > /dev/null || exit 1; \
	done
	. ./venv/bin/activate && \
	pip install --quiet -r requirements.txt -r test-requirements.txt && \
	cd src && \
        PYTHONPATH=$(PWD)/src pytest ../tests/test*.py

fmt:
	black $(find src -name *.py) tests/*.py

dist:

deploy-lambda: deploy
	@set -x ;if aws cloudformation get-template-summary --stack-name $(NAME) >/dev/null 2>&1 ; then \
		export CFN_COMMAND=update; \
	else \
		export CFN_COMMAND=create; \
	fi ;\
	aws cloudformation $$CFN_COMMAND-stack \
		--capabilities CAPABILITY_IAM \
		--stack-name $(NAME) \
		--template-body file://cloudformation/aws-cloudwatch-log-minder.yaml \
		--parameters ParameterKey=CFNCustomProviderZipFileName,ParameterValue=lambdas/$(NAME)-$(VERSION).zip; \
	aws cloudformation wait stack-$$CFN_COMMAND-complete --stack-name $(NAME) ;

delete-lambda:
	aws cloudformation delete-stack --stack-name $(NAME)
	aws cloudformation wait stack-delete-complete  --stack-name $(NAME)

demo: 
	@if aws cloudformation get-template-summary --stack-name $(NAME)-demo >/dev/null 2>&1 ; then \
		export CFN_COMMAND=update; export CFN_TIMEOUT="" ;\
	else \
		export CFN_COMMAND=create; export CFN_TIMEOUT="--timeout-in-minutes 10" ;\
	fi ;\
	export VPC_ID=$$(aws ec2  --output text --query 'Vpcs[?IsDefault].VpcId' describe-vpcs) ; \
        export SUBNET_IDS=$$(aws ec2 --output text --query 'RouteTables[?Routes[?DestinationCidrBlock == `0.0.0.0/0` && GatewayId]].Associations[].SubnetId' \
                                describe-route-tables --filters Name=vpc-id,Values=$$VPC_ID | tr '\t' ','); \
	echo "$$CFN_COMMAND demo in default VPC $$VPC_ID, subnets $$SUBNET_IDS" ; \
        ([[ -z $$VPC_ID ]] || [[ -z $$SUBNET_IDS ]] ) && \
                echo "Either there is no default VPC in your account or there are no subnets in the default VPC" && exit 1 ; \
	aws cloudformation $$CFN_COMMAND-stack --stack-name $(NAME)-demo \
		--template-body file://cloudformation/demo-stack.yaml  \
		$$CFN_TIMEOUT \
		--parameters 	ParameterKey=VPC,ParameterValue=$$VPC_ID \
				ParameterKey=Subnets,ParameterValue=\"$$SUBNET_IDS\" ;\
	aws cloudformation wait stack-$$CFN_COMMAND-complete --stack-name $(NAME)-demo ;


delete-demo:
	aws cloudformation delete-stack --stack-name $(NAME)-demo
	aws cloudformation wait stack-delete-complete  --stack-name $(NAME)-demo

