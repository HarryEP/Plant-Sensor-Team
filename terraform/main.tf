terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
    region = "eu-west-2"
}


resource "aws_security_group" "allow-traffic-to-db"{
    name = "plants-vs-trainees-database"
    vpc_id = "vpc-0e0f897ec7ddc230d"
    ingress {
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    egress {
        from_port        = 0
        to_port          = 0
        protocol         = "-1"
        cidr_blocks      = ["0.0.0.0/0"]
  }
}


resource "aws_security_group" "allow-traffic-to-dashboard"{
    name = "plants-vs-trainees-dashboard"
    vpc_id = "vpc-0e0f897ec7ddc230d"
    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "http"
        cidr_blocks = ["0.0.0.0/0"]
    }
    egress {
        from_port        = 5432
        to_port          = 5432
        protocol         = "tcp"
        cidr_blocks      = ["0.0.0.0/0"]
    }
}


resource "aws_db_instance" "db-plants" {
  identifier = "plants-vs-trainees-db"
  allocated_storage    = 5
  db_name              = "plant_monitor"
  db_subnet_group_name = "public_subnet_group"
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  username             = var.db_username
  password             = var.db_password
  publicly_accessible  = true
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.allow-traffic-to-db.id]
}


resource "aws_s3_bucket" "bucket" {
  bucket = "plants-vs-trainees-long-term-storage"
}


resource "aws_ecs_cluster" "cluster" {
  name = "plants-vs-trainees-cluster"
}


resource "aws_ecr_repository" "pipeline-repository" {
    name = "plants-vs-trainees-pipeline-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
        scan_on_push = true
    }
}


resource "aws_ecr_repository" "dashboard-repository" {
    name = "plants-vs-trainees-dashboard-ecr"
    image_tag_mutability = "MUTABLE"
    image_scanning_configuration {
        scan_on_push = true
    }
}


resource "aws_iam_role" "ecs_role" {
  name = "ecs_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_ecs_task_definition" "dashboard-task-definition" {
  family                = "plants-vs-trainees-dashboard-definition"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "0.5GB"
  task_role_arn            = aws_iam_role.ecs_role.arn
  execution_role_arn= "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  container_definitions = jsonencode(
[
  {
    "name": "c8-ieva-tf-dashboard",
    "image": "${aws_ecr_repository.dashboard-repository.url}:latest",
    "essential": true,
    "portMappings": [
      {
        "containerPort": 8501,
        "hostPort": 8501
      }
    ],
    "environment" : [
        {"name" : "DB_PASSWORD", "value" : var.db_password},
        {"name" : "DB_USER", "value" : var.db_username},
        {"name" : "DB_PORT", "value" : var.db_port},
        {"name" : "DB_NAME", "value" : var.db_name},
        {"name" : "ACCESS_KEY_ID", "value" : var.access_key_id},
        {"name" : "SECRET_ACCESS_KEY", "value" : var.secret_access_key},
        {"name" : "DB_HOST", "value" : var.db_host},
        {"name" : "DB_SCHEMA", "value" : var.db_schema}
      ]
  }
]
)
}


resource "aws_ecs_task_definition" "name" {

}

resource "aws_ecs_service" "c8-pvst-pipeline-ecs" {

}



