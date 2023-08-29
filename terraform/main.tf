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
    name = "c8-plants-vs-trainees-sg"
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
        ipv6_cidr_blocks = ["::/0"]
  }
}


resource "aws_db_instance" "db-plants" {
  identifier = "c8-plants-vs-trainees-db"
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


resource "aws_s3_bucket" "c8-plants-vs-trainees" {
  bucket = "c8-plants-vs-trainees"
}