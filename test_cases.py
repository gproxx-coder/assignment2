import glob
import os
from collections import defaultdict
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
import boto3
from utils import read_log_file, logs_generator, file_writer, get_all_log_files, get_s3_client, upload_files_to_s3, \
    generate_file_name_for_s3
from typing import Generator
from boto3.s3.transfer import S3Transfer


class TestFileReader(TestCase):
    """
    This will test the reading file functionality
    """
    mock_output_loc = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        It will setup some objects required for multiple methods
        Like creating test directory if not present
        Also reading data from test files for mocking purpose
        """
        cls.logs = read_log_file('mock_data/inp/logs.md')
        cls.log_types = ['https', 'http', 'ftp']
        cls.mock_input_loc = 'mock_data/inp/log*.md'
        cls.mock_input_loc_invalid = 'mock_data/inp/log*'
        cls.mock_output_loc = 'mock_data/output/'
        cls.log_type = 'https'

        if not os.path.exists(cls.mock_output_loc):
            os.makedirs(cls.mock_output_loc)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        It will delete folder/files created during test
        """
        import shutil
        if os.path.exists(cls.mock_output_loc):
            shutil.rmtree(cls.mock_output_loc)

    def test_read_log_file(self):
        """
        It will check whether we read correct data or not
        """
        self.assertTrue(self.logs)
        self.assertIsInstance(self.logs, defaultdict)

    def test_log_generator(self):
        """
        It will check whether we receive Generator object or not
        """
        for log_type in self.log_types:
            gen = logs_generator(self.logs.get(log_type))
            self.assertTrue(gen)
            self.assertIsInstance(gen, Generator)

    def test_file_writer(self):
        """
        It will test whether the written file exists or not for all log types
        """
        for log_type in self.log_types:
            gen = logs_generator(self.logs.get(log_type))
            file_writer(gen, self.mock_output_loc, f'mock_{log_type}.md', log_type)
            self.assertTrue(os.path.exists(self.mock_output_loc + f'mock_{log_type}.md'))

    def test_get_all_log_files_valid_files(self):
        """
        It will test whether we receive all valid file names or not
        """
        mocked = set(glob.glob(self.mock_input_loc))
        log_files = set(get_all_log_files(self.mock_input_loc))
        self.assertEqual(mocked, log_files)

    def test_get_all_log_files_invalid_files(self):
        """
        It will test that we must not receive invalid file name
        Valid filenames: log.md, logs.md, log123.md, log_234.md, etc
        Invalid filename: log, log.txt, log123, log.jpg, etc
        """
        mocked = set(glob.glob(self.mock_input_loc_invalid))
        log_files = set(get_all_log_files(self.mock_input_loc))
        self.assertNotEqual(mocked, log_files)

    @patch('utils.boto3.client')
    def test_get_s3_client(self, mock_ob):
        """
        It will test that we receive S3 client object
        """
        mock_ob.return_value = boto3.client
        client = get_s3_client()
        self.assertTrue(client)

    @patch('utils.boto3.client')
    def test_get_s3_client_error(self, mock_ob):
        """
        It will test that we receive S3 client object
        """
        mock_ob.return_value = boto3.client
        client = get_s3_client()
        self.assertTrue(client)

    @patch('utils.boto3.s3.inject.S3Transfer')
    def test_upload_files_to_s3(self, mock_ctx_mgr):
        mock_ctx_mgr().__enter__().someFunc.return_value = "val"
        resp = upload_files_to_s3('logs.md', self.log_type, file_location='mock_data/inp/')
        self.assertTrue(resp)

    @patch('utils.generate_file_name_for_s3')
    def test_generate_file_name_for_s3(self, mock_ob):
        date_now, time_now = str(datetime.now()).split()
        desired = f"logs/{self.log_type}/{date_now}/{time_now}_https_logs.md"
        mock_ob.return_value = desired
        resp = generate_file_name_for_s3('https_logs.md', self.log_type)
        self.assertEqual(desired, resp)
