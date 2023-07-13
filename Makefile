export LAMBDA_NAME=mpb_lambda
export LAYER_NAME=mpb_layer
export LAYER_DESCRIPTION=mpb_layer
export LAMBDA_REGION=us-east-2
export AWS_CA_BUNDLE /Users/andrew/Downloads/mpb.pem

.DEFAULT_GOAL := all
create_layer:
	/bin/sh ./scripts/create_layer.sh

deploy_layer:
	/bin/sh ./scripts/deploy_layer.sh


create:
	/bin/sh ./scripts/create.sh

build:

	/bin/sh ./scripts/build.sh

deploy:

	/bin/sh ./scripts/deploy.sh

run:
	/bin/sh ./scripts/run.sh

all:

	make build
	make deploy
	make run