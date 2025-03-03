# AmazonConnectDeletionTool

Using Amazon Connect and need to delete call recordings in bulk? Have fun doing it manually. As Amazon don't allow for bulk record deletion, based on queue, you're stuck doing this manually. Hence, the need for a simple tool like this.

[!NOTE]
Use are your own risk, this tool has the potential to delete any and all S3 files.

### Usage
For general safety, this tool has been broken down into 2 parts, collecting all relevant call IDs and the record deletion based off of said IDs.

1. Create your .env file, this'll contain your secrets and values used by Boto3, it should match the example:
	-AWS_ACCESS_KEY: Collect from your AWS IAM profile, ensure appropriate permissions for reading and deleting from S3 and Amazon Connect
	-AWS_SECRET_KEY: Collect from AWS IAM profile
	-REGION: The region of your AC and S3 instance
	-INSTANCE_ID: ID of your Amazon Connect Instance
	-AC_QUEUES: json format of your queues to be deleted, {"q1": "arn:aws...01", etc....}
	-S3_BUCKET: Name of your S3 bucket containing your call recordings
	-PREFIX: The directory structure within your S3 bucket, only go down to whichever directory contains the recordings, i.e. "amazonconnect/company/CallRecordings"

2. Prep and activate your virtual environment with:
```
    py -m venv .venv
    .venv/Scripts/activate.ps1
    pip install -r requirements.txt
```

3. Generate your *call_id_list.csv* file by running the **get_calls.py** file
	```
	py get_calls.py path/to/env/file/.env start_month start_year end_month end_year
	```
	For example:
	```
	py get_calls.py secrets/.env 3 2023 3 2025
	```
	Would start from the first of March, 2023 to the first of March, 2025.

> [!NOTE]  
> Highlights information that users should take into account, even when skimming.

[!IMPORTANT]
Due to the limits of the Amazon Connect API, you only go up to 24 months back.
	
4. Compare the returned results within *call_id_list.csv*, to call IDs you expect to see. Ensure that only the correct call IDs are included
5. Run **delete_call_by_id.py**, with the same parameters as **get_calls.py**:
[!IMPORTANT]
**ENSURE THAT ONLY THE CORRECT CALL IDS ARE PRESENT**
```
	py delete_call_by_id.py path/to/env/file/.env start_month start_year end_month end_year
```
