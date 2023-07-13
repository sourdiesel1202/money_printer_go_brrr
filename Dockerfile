FROM public.ecr.aws/lambda/python:3.8

# Copy function code
COPY *.py ${LAMBDA_TASK_ROOT}
COPY configs/ ${LAMBDA_TASK_ROOT}
COPY data/ ${LAMBDA_TASK_ROOT}

# Copy lambda function code and install requirements
COPY . .

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
ADD . .

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG AWS_S3_ENDPOINT_URL

ENV AWS_ACCESS_KEY_ID ${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY ${AWS_SECRET_ACCESS_KEY}
ENV AWS_DEFAULT_REGION ${AWS_DEFAULT_REGION}
ENV AWS_S3_ENDPOINT_URL ${AWS_S3_ENDPOINT_URL}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]