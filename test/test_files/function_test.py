"""Unit tests for functions used in Robot Framework Historic Parser"""
import os
import sys
import unittest
from unittest.mock import patch
from mock import MagicMock
import robotframework_historic_parser.rfhistoricparser
from robotframework_historic_parser.parserargs import parse_options

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))


class TestFunctions(unittest.TestCase):
    """Unit Tests for functions"""

    def test_get_time_in_min(self):
        """This test verifies that get_time_in_min returns a time in minutes. """
        test_time = '01:02:03'
        expected_result = 62.05
        result_in_minutes = robotframework_historic_parser.rfhistoricparser.get_time_in_min(test_time)
        self.assertEqual(result_in_minutes, expected_result)

    def test_get_time_in_min_bad_input(self):
        """This test verifies that get_time_in_min returns error if invalid input is passed. """
        self.assertRaisesRegex(ValueError, 'not enough values to unpack', robotframework_historic_parser.rfhistoricparser.get_time_in_min, 'a')

    @patch('builtins.print')
    def test_rfhistoric_parser_ignore_result(self, mock_print):
        """This test verifies that the parser ignores any results if the ignore result argument
        is set to True. """
        sys.argv[1:] = ['-g', 'True']
        test_opts = parse_options()
        result = robotframework_historic_parser.rfhistoricparser.rfhistoric_parser(test_opts)
        mock_print.assert_called_with("Ignoring execution results...")
        self.assertEqual(result, None)

    def test_allure_report_parser(self):
        file_path = ROOT_PATH + "/" + "empty.xml"
        sys.argv[1:] = ['-o', file_path]
        test_opts = parse_options()
        robotframework_historic_parser.rfhistoricparser.connect_to_mysql_db = MagicMock()
        robotframework_historic_parser.rfhistoricparser.insert_into_execution_table = MagicMock()
        robotframework_historic_parser.rfhistoricparser.process_allure_report(test_opts)

    def test_rfhistoric_parser(self):
        """This test verifies that the rfhistoric parser function. """
        file_path = ROOT_PATH + "/" + "empty.xml"
        sys.argv[1:] = ['-o', file_path]
        test_opts = parse_options()
        robotframework_historic_parser.rfhistoricparser.connect_to_mysql_db = MagicMock()
        robotframework_historic_parser.rfhistoricparser.insert_into_execution_table = MagicMock()
        result = robotframework_historic_parser.rfhistoricparser.rfhistoric_parser(test_opts)
        print(result)

    # def test_rfhistoric_parser_bad_output_file(self):
    #     """This test verifies that the rfhistoric parser function. """
    #     file_path = ROOT_PATH + "/" + "empty.somebadformat"
    #     sys.argv[1:] = ['-o', file_path]
    #     test_opts = parse_options()
    #     robotframework_historic_parser.rfhistoricparser.connect_to_mysql_db = MagicMock()
    #     robotframework_historic_parser.rfhistoricparser.insert_into_execution_table = MagicMock()
    #     with self.assertRaises(SystemExit):
    #         rfhistoric_parser(test_opts)
