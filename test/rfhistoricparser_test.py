"""Unit tests for functions used in Robot Framework Historic Parser rfhistoricparser"""
import json
import sys
import unittest
from unittest import mock
from unittest.mock import patch, Mock, MagicMock
from robotframework_historic_parser.rfhistoricparser import (
    get_time_in_min,
    rfhistoric_parser,
    remove_special_characters,
    process_statistics_report,
    insert_into_execution_table,
    process_junit_report,
    process_allure_report,
)
from robotframework_historic_parser.parserargs import parse_options


class MockOpts:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestRFHistoricParser(unittest.TestCase):
    def test_get_time_in_min(self):
        # Test that the method correctly converts time strings to minutes
        self.assertAlmostEqual(get_time_in_min("00:01:00"), 1)
        self.assertAlmostEqual(get_time_in_min("01:00:00"), 60)
        self.assertAlmostEqual(get_time_in_min("00:30:30"), 30.5)

    def test_get_time_in_min_bad_input(self):
        """This test verifies that get_time_in_min returns error if invalid input is passed."""
        self.assertRaisesRegex(
            ValueError,
            "not enough values to unpack",
            get_time_in_min,
            "a",
        )

    @patch("builtins.print")  # Mock the print function to avoid actual print statements
    def test_rfhistoric_parser_ignores_result(self, mock_print):
        opts = MockOpts(ignoreresult="True")
        rfhistoric_parser(opts)
        mock_print.assert_called_once_with("Ignoring execution results...")

    @patch("os.path.exists", return_value=False)
    @patch("os.listdir", return_value=["test1.xml", "test2.xml"])
    @patch("os.path.isfile", return_value=True)
    @patch("sys.exit")
    def test_rfhistoric_parser_exits_on_missing_file(
        self, mock_exit, mock_listdir, mock_exists, mock_isfile
    ):
        opts = MockOpts(
            ignoreresult="False",
            output="*.xml",
            path="not/important",
            report_type="RF",
            host="localhost",
            port=3306,
            username="superuser",
            password="passw0rd",
            projectname="test",
        )

        with self.assertRaises(SystemExit) as cm:
            rfhistoric_parser(opts)
        self.assertIn(
            "output.xml file is missing: test1.xml, test2.xml", str(cm.exception)
        )

    @patch("mysql.connector.connect")
    @patch(
        "robotframework_historic_parser.rfhistoricparser.insert_into_execution_table"
    )
    @patch("builtins.print")
    @patch("xml.etree.ElementTree.parse")
    def test_process_allure_report_xml(
        self,
        mock_parse,
        mock_print,
        mock_insert_into_execution_table,
        mock_connect_to_mysql_db,
    ):
        opts = Mock()
        opts.output = "sample.xml"
        root = Mock()
        root.get.return_value = 1
        mock_parse.return_value.getroot.return_value = root

        process_allure_report(opts)

        mock_print.assert_called_with("INFO: Writing execution results")
        mock_connect_to_mysql_db.return_value.close.assert_called_once()

    @patch("mysql.connector.connect")
    @patch(
        "robotframework_historic_parser.rfhistoricparser.insert_into_execution_table"
    )
    @patch("builtins.print")
    @patch("json.load")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_process_allure_report_json(
        self,
        mock_open,
        mock_load,
        mock_print,
        mock_insert_into_execution_table,
        mock_connect_to_mysql_db,
    ):
        opts = Mock()
        opts.output = "sample.json"
        data = {
            "statistic": {
                "total": 10,
                "passed": 1,
                "failed": 2,
                "unknown": 3,
                "skipped": 4,
            }
        }
        mock_load.return_value = data
        mock_open.return_value.read.return_value = json.dumps(data)

        process_allure_report(opts)

        mock_insert_into_execution_table.assert_called_once_with(
            mock_connect_to_mysql_db.return_value,
            mock_connect_to_mysql_db.return_value,
            opts.executionname,
            10,
            1,
            5,
            "0",
            0,
            0,
            0,
            4,
            0,
            opts.projectname,
        )
        mock_print.assert_called_with("INFO: Writing execution results")
        mock_connect_to_mysql_db.return_value.close.assert_called_once()

    @patch('builtins.print')
    def test_process_allure_report_invalid_file_type(self, mock_print):
        opts = Mock()
        opts.output = 'sample.txt'

        process_allure_report(opts)

        mock_print.assert_called_with("Invalid file type. Please provide either .xml or .json file.")


    @patch("mysql.connector.connect")
    @patch(
        "robotframework_historic_parser.rfhistoricparser.insert_into_execution_table"
    )
    @patch("xml.etree.ElementTree.parse")
    @patch("builtins.print")
    @patch(
        "builtins.open",
        unittest.mock.mock_open(
            read_data='<testsuite tests="5" failures="2" errors="1" skipped="1" time="2.5"></testsuite>'
        ),
    )
    def test_process_junit_report(self, mock_print, mock_parse, mock_insert, mock_conn):
        # Mock the database connection function
        mock_cursor = mock.Mock()
        mock_conn.cursor.return_value = mock_cursor

        # Set up the opts object
        opts = MockOpts(
            output="test.json",
            executionname="test_execution",
            host="localhost",
            port=3306,
            username="superuser",
            password="passw0rd",
            projectname="test",
        )

        process_junit_report(opts)

        mock_insert.assert_called_with(
            mock_conn.return_value,
            mock_conn.return_value,
            "test_execution",
            1,
            -2,
            2,
            1.0,
            0,
            0,
            0,
            1,
            0,
            "test",
        )
        mock_conn.return_value.close.assert_called_once()
        mock_print.assert_called_with("INFO: Writing execution results")
        self.assertEqual(1, mock_insert.call_count)

    @patch(
        "robotframework_historic_parser.rfhistoricparser.insert_into_execution_table"
    )
    @patch("mysql.connector.connect")
    @patch("builtins.print")
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_process_statistics_report(
        self, mock_open, mock_print, mock_conn, mock_insert
    ):
        # Mock the database connection function
        mock_cursor = mock.Mock()
        mock_conn.cursor.return_value = mock_cursor

        # Set up the mock data for the JSON file
        mock_data = {
            "property": [
                {"name": "PassedTestCount", "value": "10"},
                {"name": "FailedTestCount", "value": "2"},
                {"name": "TotalTestCount", "value": "12"},
            ]
        }
        mock_open.return_value.read.return_value = json.dumps(mock_data)

        # Set up the opts object
        opts = MockOpts(
            output="test.json",
            executionname="test_execution",
            host="localhost",
            port=3306,
            username="superuser",
            password="passw0rd",
            projectname="test",
        )

        # Call the function to test
        process_statistics_report(opts)

        # Assert the expected calls and behavior
        mock_print.assert_called_with("INFO: Writing statistics results")
        self.assertEqual(1, mock_insert.call_count)

    @patch("builtins.print")
    def test_process_statistics_report_invalid_json(self, mock_print):
        opts = MagicMock(output="mock_output.txt")

        # Call the function to test
        process_statistics_report(opts)

        # Assert the expected calls and behavior
        mock_print.assert_called_with("Invalid file type. Please provide a .json file.")

    def test_remove_special_characters_basic(self):
        result = remove_special_characters("Hello, World!")
        self.assertEqual(result, "Hello World")

    def test_remove_special_characters_empty_string(self):
        result = remove_special_characters("")
        self.assertEqual(result, "")

    def test_remove_special_characters_no_special_characters(self):
        result = remove_special_characters("Python3")
        self.assertEqual(result, "Python3")

    def test_remove_special_characters_with_numbers(self):
        result = remove_special_characters("Test123!@#")
        self.assertEqual(result, "Test123")

    def test_remove_special_characters_with_spaces(self):
        result = remove_special_characters("Remove these special characters!")
        self.assertEqual(result, "Remove these special characters")
