FROM amazon/aws-lambda-python

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

COPY placeholder.txt .

RUN  pip3 install -r requirements.txt

COPY main.py .

CMD [ "main.handler" ]