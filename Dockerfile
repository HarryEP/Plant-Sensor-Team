FROM amazon/aws-lambda-python

COPY requirements.txt .

RUN pip3 install -r requirements.txt 

COPY lambda.py .

CMD ["lambda.lambda_handler"]