aws lambda update-function-code \
  --function-name "${LAMBDA_NAME}" \
  --zip-file fileb://function.zip \
  --layers "arn:aws:lambda:us-east-2:930434383393:layer:mpb_dependencies_layer:1" "arn:aws:lambda:us-east-2:930434383393:layer:mpb_layer:1" \
  --region="${LAMBDA_REGION}" \
  | jq ".LastUpdateStatusReason" -r

aws lambda wait function-updated \
  --function-name "${LAMBDA_NAME}" \
  --region="${LAMBDA_REGION}"
@echo "The function has been deloyed."
  aws lambda invoke \
  --function-name "${LAMBDA_NAME}" \
  --region="${LAMBDA_REGION}" out \
  --log-type Tail \
  | jq ".LogResult" -r | base64 -d