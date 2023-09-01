# LMNH Plant-Sensor Project

What the project is for
How to install any necessary dependencies
What environment information is required
How to run the project

## Intro

This project aims to create a ETL pipeline for processing plant sensor data for the new LMNH botanical wing.
From start to finish this pipeline will download JSON data from the museum's plant data API, format and clean the data of erroneous values,
and then upload the data to a RDS database.

Recordings will stay in the database for 24 hours before being moved to an S3 bucket for long term storage in the form of a csv file.

A Streamlit dashboard is also created to visualise the data and track the plant health for the museum, this is hosted on AWS.

## Setup

Ensure that you have [Docker](https://www.docker.com/) installed and open

Please run the following to setup your database locally:\
`psql -d postgres -f create_tables.sql`

Please run the following command to install the required libraries:\
`pip3 install -r all_requirements.txt`

Also add an .env file with the following variables:

```
ACCESS_KEY_ID (for AWS)
SECRET_ACCESS_KEY (for AWS)
DB_USERNAME (Postgres)
DB_PASSWORD
DB_PORT (The port you are running the database on)
DB_NAME
DB_HOST
API_TOKEN (trefle.io API Token - the signup is free)
```

## Running the project

### Locally

Update your `.env` variables to run locally.

Build the Docker image using `docker build -t PIPELINE_NAME --platform "linux/amd64" .`\

Run the Docker image using `docker run -it --env-file .env PIPELINE_NAME`

### Cloud

#### Set up cloud resources

Update `.env` file to use your AWS details and RDS url.

Enter relevant values for the variables in `variables.tf` in a `terraform.tfvars` file (should match `.env`).
Run the following commands in the `terraform` directory to set up the AWS cloud resources and enter `yes`:
`terraform init`
`terraform apply`
To remove all cloud resources run and enter `yes`:
`terraform destroy`

#### Building docker images

Create the necessary Docker images by navigating to the dashboard/lambda/pipeline folders, respectively, and running:
`docker build -t [FOLDER_NAME] --platform 'linux/amd64' .`
Follow the steps on AWS ECR to push each docker image to the ECR.

#### Running the ECS services

The structures set up by Terraform will deploy automatically to the `plants-vs-trainees-cluster` cluster. The pipeline service will carry out under `plants-vs-trainees-pipeline-service`, whilst the dashboard service will run under `plants-vs-trainees-dashboard-service`.
If changes are made to the ECRs, a need revision on the ECS task definition and new deployment on ECS Service may be needed.

#### Running lambda

EventBridge will trigger the lambda every 24 hours.
This lambda will upload data from the RDS of past 24 hours readings to the s3 bucket.

Run the following command: `python3 main.py`

#### Dashboard

To visit the dashboard _on the cloud_, go to `http://3.10.52.101:8501/`.

To run the dashboard locally use the command: `streamlit run dashboard.py`\

To visit the dashboard locally go to the [link](http://localhost:8501/) Streamlit outputs in the terminal.

Dashboard preview:
![Dashboard preview](image.png)
On the left toolbar, you may select one or more plants for display, as well as the time period.
If only one plant is selected, a picture will appear at the bottom of the page.
In order to see the graphs, you must select the plants you want and the time period you want.

![Dashboard preview](image-1.png)
