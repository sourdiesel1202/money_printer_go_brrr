  aws lambda create-function \
  --function-name "${LAMBDA_NAME}" \
  --region "${LAMBDA_REGION}"  \
  --zip-file fileb://function.zip \
  --handler lambda_function.lambda_handler \
  --runtime python3.9 \
  --role arn:aws:iam::930434383393:role/service-role/search_strain_by_name-role-w7ktdpcu
