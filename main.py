import sys
from utils import *
from botocore.exceptions import ClientError, NoCredentialsError


def main():
    """
    This is main driver function which will trigger the execution
    It will perform below operations:
    1. Fetch the list of valid log filenames (pattern- log*.md)
    2. Read input log file one by one
    3. Pop url types (https, http, ftp) from dictionary and create generator for the list
    4. Write logs of same type to different files
    5. Upload files to S3 bucket in respective folders
    """

    # Fetching all valid filenames
    all_log_files = get_all_log_files()

    # We have these 3 log types
    log_types = ['https', 'http', 'ftp']
    local_output_path = 'output'

    # Running loop for each input file
    # This task can be also given to multiple processes
    # Or we can also use celery workers to perform this task in parallel
    for log_file in all_log_files:
        logs = read_log_file(log_file)

        for log_type in log_types:
            log_ = logs.pop(log_type) if logs.get(log_type) else None
            if log_:
                # Creating a generator
                log_gen = logs_generator(log_)

                # Writing file to local
                try:
                    file_writer(log_gen, local_output_path, f'{log_type}_logs.md', log_type)
                except FileNotFoundError as e:
                    print(e)
                    sys.exit(1)

                # Uploading file to S3
                print(f"Uploading {log_type}_logs.md file to S3...")
                try:
                    upload_files_to_s3(f'{log_type}_logs.md', log_type)
                except ClientError as e:
                    # This will catch client errors such as
                    # Invalid access_key_id, secret_access_key
                    # also bucket permissions, access denied, etc
                    print(e)
                    sys.exit(1)
                except NoCredentialsError as e:
                    print("Unable to locate credentials (aws_access_key_id & aws_secret_access_key) !!")
                    print("Please check readme.md for instructions to configure aws credentials")
                    print(e)
                    sys.exit(1)
                except Exception as e:
                    print("Failed to upload the file. Something went wrong.")
                    print(e)
                    sys.exit(1)


if __name__ == '__main__':
    main()
