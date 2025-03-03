import os
import json
import boto3
import sys
import time
import random
import argparse
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from dotenv import load_dotenv

def get_all_call_ids(instance_id, queue_ids, start_time, end_time):
    """
    Fetches all unique call IDs from Amazon Connect within a given time range.
    Handles pagination using NextToken and implements rate limiting with backoff.
    """
    output_file = open('call_id_list.csv','a')

    call_ids = set()
    next_token = None
    base_delay = 1  # Base delay in seconds between API calls

    while True:
        params = {
            "InstanceId": instance_id,
            "TimeRange": {
                "Type": "INITIATION_TIMESTAMP",
                "StartTime": start_time,
                "EndTime": end_time
            },
            "SearchCriteria": {
                "QueueIds": queue_ids
            },
            "Sort": {
                "FieldName": "INITIATION_TIMESTAMP",
                "Order": "ASCENDING"
            }
        }
        
        if next_token:
            params["NextToken"] = next_token  # Add pagination token if present
        
        # Add delay between API calls to avoid rate limiting
        time.sleep(base_delay)
        
        # Implement exponential backoff for retries
        max_retries = 5
        retry_count = 0
        retry_delay = base_delay
        
        while retry_count < max_retries:
            try:
                response = client.search_contacts(**params)
                break  # Break out of retry loop if successful
            except ClientError as e:
                if e.response['Error']['Code'] == 'TooManyRequestsException':
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise  # Re-raise if max retries reached
                    
                    # Calculate backoff with jitter
                    jitter = random.uniform(0, 0.1 * retry_delay)
                    sleep_time = retry_delay + jitter
                    time.sleep(sleep_time)
                    
                    # Exponential backoff
                    retry_delay *= 2
                else:
                    raise  # Re-raise if it's a different error

        # Iterate through retrieved contacts
        for record in response.get("Contacts", []):
            call_id = record["Id"]
            call_ids.add(call_id)
            output_file.write(f"{call_id}\n")
            print(f"{call_id}")

        next_token = response.get("NextToken")
        if not next_token:
            break  # Stop if no more pages

    return call_ids

def get_call_ids_for_two_years(instance_id, queue_ids, start_year, start_month):
    """
    Iterates over 8-week chunks for 2 years to collect all call IDs.
    """
    call_ids = set()
    start_date = datetime(start_year, start_month, 1)
    final_date = start_date + timedelta(weeks=104)  # 2 years later

    while start_date < final_date:
        end_date = min(start_date + timedelta(weeks=8), final_date)  # Ensure we don't exceed 2 years

        # Fetch call IDs for this 8-week period
        call_ids.update(get_all_call_ids(instance_id, queue_ids, start_date, end_date))

        # Move to the next 8-week period
        start_date = end_date

    return call_ids

def main():
    
    args_parser = argparse.ArgumentParser(description="idk")

    args_parser.add_argument(
        "env_file_path",
        type=str,
        help='Path to your .env file, contains your AWS secrets and IDs',
    )
    args_parser.add_argument(
        "start_month",
        type=str,
        help='Start month (1-12)'
    )
    args_parser.add_argument(
        "start_year",
        type=str,
        help='Start year, must be within 2 years from current date'
    )
    args_parser.add_argument(
        "end_month",
        type=str,
        help='End month (1-12)'
    )
    args_parser.add_argument(
        "end_year",
        type=str,
        help='End year',
    )

    args = args_parser.parse_args()









    load_dotenv(args.env_file_path)

    client = boto3.client(
        "connect",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("REGION"),
    )
    # instance_id = os.getenv("INSTANCE_ID")
    # queue_ids = list(json.loads(os.getenv("AC_QUEUES")).values())

    # start_year = 2023
    # start_month = 4
    # all_call_ids = get_call_ids_for_two_years(instance_id, queue_ids, start_year, start_month)

if __name__ == "__main__":
    main()