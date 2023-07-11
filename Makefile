export LAMBDA_NAME=MPB_Alerting1
export LAMBDA_REGION=us-east-2

.DEFAULT_GOAL := all

build:
	pip3 install -r requirements.txt \
		--platform manylinux2014_x86_64 \
		--target=. \
		--implementation cp \
		--python 3.9 \
		--only-binary=:all: --upgrade

deploy:
	zip -r function.zip ./
	aws lambda update-function-code \
		--function-name "${LAMBDA_NAME}" \
		--zip-file fileb://function.zip \
		--region="${LAMBDA_REGION}" \
		| jq ".LastUpdateStatusReason" -r
	aws lambda wait function-updated \
		--function-name "${LAMBDA_NAME}" \
		--region="${LAMBDA_REGION}"
	@echo "The function has been deloyed."

run:
	aws lambda invoke \
		--function-name "${LAMBDA_NAME}" \
		--region="${LAMBDA_REGION}" out \
		--log-type Tail \
		| jq ".LogResult" -r | base64 -d

all:
	make build
	make deploy
	make run