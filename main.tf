provider "aws" { 
  region = "eu-north-1"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "customersegbuck"
}

resource "aws_instance" "custsegec2" {
  ami           = "ami-0368b2c10d7184bc7"
  instance_type = "t3.micro"
  key_name      = "awskey"
  subnet_id     = "subnet-03567b93b26f9185b"  # Specify a subnet from your VPC

  tags = {
    Name = "CustomerSegmentationEC2"
  }
}

# DynamoDB Table for storing clustering results
resource "aws_dynamodb_table" "customer_segmentation_table" {
  name           = "customer-segmentation-table"
  hash_key       = "n_clusters"
  billing_mode   = "PAY_PER_REQUEST"  # Use on-demand billing for free tier

  attribute {
    name = "n_clusters"
    type = "N"  # Numeric type for n_clusters
  }

  attribute {
    name = "centroids"
    type = "S"  # String type for centroids (you can store them as JSON)
  }

  # Global Secondary Index for centroids attribute
  global_secondary_index {
    name               = "centroids-index"
    hash_key           = "centroids"
    projection_type    = "ALL"  # Can also be "KEYS_ONLY" or "INCLUDE"
    read_capacity      = 5
    write_capacity     = 5
  }

  # Optionally, you can add more indexes or additional attributes as needed
}
