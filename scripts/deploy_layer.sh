aws lambda publish-layer-version --layer-name "${LAYER_NAME}" \
    --description "${LAYER_DESCRIPTION}" \
    --license-info "MIT" \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.7 python3.8 \
    --compatible-architectures "arm64" "x86_64"
