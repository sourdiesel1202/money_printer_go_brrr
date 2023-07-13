  aws lambda invoke \
  --function-name "${LAMBDA_NAME}" \
  --region="${LAMBDA_REGION}" out \
  --log-type Tail \
  | jq ".LogResult" -r | base64 -d