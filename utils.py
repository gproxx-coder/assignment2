import glob
import os
from collections import defaultdict
from datetime import datetime
import boto3
from typing import Dict, List, Generator


BUCKET_NAME = 'project-logs-bucket'
LOG_FILES_LOCATION = 'project-folder\\logs\\log*.md'
OUTPUT_LOCATION = 'output\\'


def get_s3_client():
    # return boto3.client(
    #     's3',
    #     aws_access_key_id=os.environ.get('<Your Access Key ID>'),
    #     aws_secret_access_key=os.environ.get('<Your Secret Access Key>')
    # )

    # Please remove aws_access_key_id & aws_secret_access_key if you are using aws cli configurations
    return boto3.client(
        's3',
        aws_access_key_id='<Your Access Key ID>',
        aws_secret_access_key='<Your Secret Access Key>'
    )


s3_client = get_s3_client()


def get_all_log_files(loc: str = LOG_FILES_LOCATION) -> List:
    """
    This function will return list of log files present in ./project-folder/logs/ folder
    It will pick files that start with 'log' (e.g. log1.md, log,md, log123.md, etc)
    It will pick file that ends with .md ONLY. not other files.
    :param loc:
    :return:
    """
    return glob.glob(loc)


def read_log_file(log_filename: str) -> Dict:
    """
    This function will read log file from local directory
    and returns dict with 3 categories/keys (https, http, ftp)
    :param log_filename: input local log file name
    :return: Dictionary with 3 keys (https, http, ftp)
    """
    counter = defaultdict(list)
    with open(log_filename, 'r') as logfile:
        https, http, ftp = 'https', 'http', 'ftp'
        for line in logfile:
            if line[:8] == 'https://':
                counter[https].append(line)
            elif line[:7] == 'http://':
                counter[http].append(line)
            elif line[:6] == 'ftp://':
                counter[ftp].append(line)
    return counter


def logs_generator(logs: List) -> Generator:
    """
    Return an object that produces a sequence of URLs of same type
    :param logs: List of URL of same type
    :yield:
    """
    for log in logs:
        yield log


def file_writer(gen: Generator, path: str, file_name: str, log_type: str) -> None:
    """
    This function will get URL from generator function one by one
    and will pass it to writelines function so that it will write lines at once
    :param gen: Generator object
    :param path: Path where file needs to be written
    :param file_name: file name of the file
    :param log_type: type of log (https, http or ftp)
    :return: None
    """
    if not os.path.exists(path):
        os.makedirs(path)

    with open(f'{path}/{file_name}', 'w') as logfile:
        logfile.writelines(gen)


def generate_file_name_for_s3(file_to_upload: str, log_type: str) -> str:
    """
    This function will generate fully qualified file name for S3 bucket
    :param file_to_upload: filename to be uploaded
    :param log_type: type of log (https, http or ftp)
    :return:
    """
    date_now, time_now = str(datetime.now()).split()
    return f"logs/{log_type}/{date_now}/{time_now}_{file_to_upload}"


def upload_files_to_s3(file_to_upload: str, log_type: str, **kwargs) -> bool:
    """
    This function will upload file to S3 bucket mentioned in global variable- BUCKET_NAME
    :param file_to_upload: filename to be uploaded
    :param log_type: type of log (https, http or ftp)
    :param kwargs - file_location, filename_s3
    :return:
    """

    if kwargs.get('file_location'):
        file_location = kwargs.get('file_location')
    else:
        file_location = OUTPUT_LOCATION

    if kwargs.get('filename_s3'):
        filename_s3 = kwargs.get('filename_s3')
    else:
        filename_s3 = generate_file_name_for_s3(file_to_upload, log_type)

    s3_client.upload_file(file_location + file_to_upload, BUCKET_NAME, filename_s3)
    return True
