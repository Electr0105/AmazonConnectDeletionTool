import os
import sys
import csv
import boto3
from dotenv import load_dotenv
from datetime import datetime, timedelta

env_path = sys.argv[1]
load_dotenv(env_path)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("REGION"),
)

def load_contact_ids(csv_file):
    contact_ids = set()

    with open(csv_file, mode="r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            contact_ids.add(row[0])  # Assuming Contact ID is in the first column
    return contact_ids

def list_s3_objects(bucket_name, prefix):
    """Lists all objects in a specified S3 bucket folder."""

    objects = []
    paginator = s3_client.get_paginator("list_objects_v2")
    
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            objects.append(obj["Key"])  # Store full file path
    return objects

def delete_matching_files(bucket_name, contact_ids, start_date, end_date):
    """Deletes S3 files that match Contact IDs within a date range."""
    base_prefix = os.getenv("PREFIX")
    files_deleted = 0
    # Loop through each day in the given date range
    current_date = start_date
    while current_date <= end_date:
        year, month, day = current_date.strftime("%Y"), current_date.strftime("%m"), current_date.strftime("%d")
        prefix = f"{base_prefix}{year}/{month}/{day}/"

        # List files in the current date folder
        objects = list_s3_objects(bucket_name, prefix)

        for file_key in objects:
            file_name = file_key.split("/")[-1]  # Extract filename from path
            contact_id = file_name.split("_")[0]  # Extract Contact ID before first underscore
            if contact_id in contact_ids:
                print(f"Deleting: {file_key}")  # Debugging message
                s3_client.delete_object(Bucket=bucket_name, Key=file_key)
                files_deleted += 1

        # Move to the next day
        current_date += timedelta(days=1)

    print(f"Total files deleted: {files_deleted}")

def main():
    bucket_name = os.getenv("S3_BUCKET")
    csv_file = "output.csv"

    start_date = datetime(2023, 4, 3)  # Example start date
    end_date = datetime(2025, 3, 3)  # Example end date

    contact_ids = load_contact_ids(csv_file)
    delete_matching_files(bucket_name, contact_ids, start_date, end_date)

if __name__ == "__main__":
    main()