"""Unit tests for functions used in Robot Framework Historic Parser rfhistoricparser"""
import json
import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch, Mock, MagicMock, call
from robotframework_historic_parser.rfhistoricparser import (
    get_time_in_min,
    rfhistoric_parser,
    remove_special_characters,
    process_statistics_report,
    insert_into_execution_table,
    process_junit_report,
    process_allure_report,
    commit_and_close_db,
    ExecutionResult,
    datetime,
    SuiteStats,
    SuiteResults,
    TestMetrics,
)
from robotframework_historic_parser.parserargs import parse_options

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

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
    def test_rfhistoric_parser_rf7(self, mock_insert, mock_conn):
        file_path = ROOT_PATH + "/" + "test_files/output_test_rf7.xml"
        opts = MockOpts(
            ignoreresult="False",
            output=file_path,
            path="",
            report_type="RF",
            host="localhost",
            port=3306,
            username="superuser",
            password="passw0rd",
            projectname="test",
            executionname="test_executionname",
            fullsuitename="test_fullsuitename",
        )
        rfhistoric_parser(opts)
        assert mock_insert.call_args.args[2:] == (
            "test_executionname",
            3,
            1,
            1,
            0.0,
            1,
            0,
            1,
            1,
            0,
            "test",
        )

    @patch("mysql.connector.connect")
    @patch(
        "robotframework_historic_parser.rfhistoricparser.insert_into_execution_table"
    )
    def test_rfhistoric_parser_rf6(self, mock_insert, mock_conn):
        file_path = ROOT_PATH + "/" + "test_files/output_test_rf6.xml"
        opts = MockOpts(
            ignoreresult="False",
            output=file_path,
            path="",
            report_type="RF",
            host="localhost",
            port=3306,
            username="superuser",
            password="passw0rd",
            projectname="test",
            executionname="test_executionname",
            fullsuitename="test_fullsuitename",
        )
        rfhistoric_parser(opts)
        assert mock_insert.call_args.args[2:] == (
            "test_executionname",
            3,
            1,
            1,
            0.0,
            1,
            0,
            1,
            1,
            0,
            "test",
        )

    @patch("mysql.connector.connect")
    @patch("robotframework_historic_parser.rfhistoricparser.ExecutionResult")
    @patch(
        "robotframework_historic_parser.rfhistoricparser.insert_into_execution_table"
    )
    @patch("robotframework_historic_parser.rfhistoricparser.commit_and_close_db")
    @patch("builtins.print")
    @patch("os.listdir", return_value=["output.xml"])
    @patch(
        "os.path.exists", return_value=True
    )  # Mocking os.path.exists to always return True
    def test_rfhistoric_parser_rf(
        self,
        mock_exists,
        mock_listdir,
        mock_print,
        mock_commit_and_close_db,
        mock_insert_into_execution_table,
        mock_ExecutionResult,
        mock_connect_to_mysql_db,
    ):
        opts = Mock()
        opts.ignoreresult = "False"
        opts.path = "/some/path"
        opts.output = "*.xml"
        opts.report_type = "RF"
        opts.host = "test_host"
        opts.port = "test_port"
        opts.username = "test_username"
        opts.password = "test_password"
        opts.projectname = "test_project"
        opts.executionname = "test_executionname"
        opts.fullsuitename = "test_fullsuitename"

        mock_result = mock_ExecutionResult.return_value
        mock_result.suite.elapsedtime = 1000  # assuming elapsed time in milliseconds
        mock_test_stats = Mock()
        mock_test_stats.total_suite = 10
        mock_test_stats.passed_suite = 7
        mock_test_stats.failed_suite = 2
        mock_test_stats.skipped_suite = 1
        mock_result.statistics.total.all = mock_test_stats

        with patch(
            "robotframework_historic_parser.rfhistoricparser.datetime"
        ) as mock_datetime, patch(
            "robotframework_historic_parser.rfhistoricparser.get_time_in_min"
        ) as mock_gettime:
            mock_datetime.timedelta.return_value = Mock()
            mock_gettime.return_value = 10
            rfhistoric_parser(opts)

        mock_ExecutionResult.assert_called_once_with()
        mock_result.configure.assert_called_once_with(
            stat_config={"suite_stat_level": 2, "tag_stat_combine": "tagANDanother"}
        )
        self.assertEqual(3, mock_result.visit.call_count)
        mock_commit_and_close_db.assert_called_once()

        expected_calls = [
            call("INFO: Capturing suite results"),
            call("INFO: Capturing test results"),
            call("INFO: Writing execution results"),
        ]

        mock_print.assert_has_calls(expected_calls, any_order=True)

    @patch("robotframework_historic_parser.rfhistoricparser.process_junit_report")
    @patch("os.listdir", return_value=["output.xml"])
    @patch("builtins.exit")
    def test_rfhistoric_parser_junit(
        self, mock_exit, mock_list, mock_process_junit_report
    ):

        opts = Mock()
        opts.report_type = "junit"
        opts.path = "/some/path"
        opts.output = "*.xml"

        with patch("builtins.print"):
            rfhistoric_parser(opts)

        mock_process_junit_report.assert_called_once_with(opts)
        mock_exit.assert_not_called()

    @patch("robotframework_historic_parser.rfhistoricparser.process_allure_report")
    @patch("os.listdir", return_value=["output.xml"])
    @patch("builtins.exit")
    def test_rfhistoric_parser_allure(
        self, mock_exit, mock_list, mock_process_allure_report
    ):

        opts = Mock()
        opts.report_type = "Allure"
        opts.path = "/some/path"
        opts.output = "*.xml"

        with patch("builtins.print"):
            rfhistoric_parser(opts)

        mock_process_allure_report.assert_called_once_with(opts)
        mock_exit.assert_not_called()

    @patch("robotframework_historic_parser.rfhistoricparser.process_allure_report")
    @patch("builtins.exit")
    @patch("os.path.exists", return_value=True)
    def test_rfhistoric_parser_allure(
        self, mock_path, mock_exit, mock_process_allure_report
    ):
        opts = Mock()
        opts.report_type = "Allure"
        opts.path = "/some/path"
        opts.output = "sample.txt"

        with patch("builtins.print"):
            rfhistoric_parser(opts)

        # Verify that process_allure_report was called with the correct arguments
        mock_process_allure_report.assert_called_once_with(opts)

        # Verify that exit was not called
        mock_exit.assert_not_called()

    @patch("robotframework_historic_parser.rfhistoricparser.process_statistics_report")
    @patch("builtins.exit")
    @patch("os.path.exists", return_value=True)
    def test_rfhistoric_parser_statistics(
        self, mock_path, mock_exit, mock_process_statistics_report
    ):
        opts = Mock()
        opts.report_type = "Statistics"
        opts.path = "/some/path"
        opts.output = "sample.txt"

        rfhistoric_parser(opts)

        mock_process_statistics_report.assert_called_once_with(opts)
        mock_exit.assert_not_called()

    @patch("builtins.exit")
    def test_rfhistoric_parser_invalid_report_type(self, mock_exit):
        opts = Mock()
        opts.report_type = "InvalidType"
        opts.path = "/some/path"
        opts.output = "sample.txt"

        rfhistoric_parser(opts)

        mock_exit.assert_called_with("report_type of InvalidType is not supported.")

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
            2,
            "0",
            0,
            0,
            0,
            7,
            0,
            opts.projectname,
        )
        mock_print.assert_called_with("INFO: Writing execution results")
        mock_connect_to_mysql_db.return_value.close.assert_called_once()

    @patch("builtins.print")
    def test_process_allure_report_invalid_file_type(self, mock_print):
        opts = Mock()
        opts.output = "sample.txt"

        process_allure_report(opts)

        mock_print.assert_called_with(
            "Invalid file type. Please provide either .xml or .json file."
        )

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
                {"name": "SkippedTestCount", "value": "3"},
                {"name": "TotalTestCount", "value": "15"},
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



    def test_suite_stats_passed_suite(self):
        """Test SuiteStats with passed status"""
        suite_stats = SuiteStats()
        
        # Create a mock suite with PASS status
        mock_suite = Mock()
        mock_suite.tests = [Mock()]  # Has tests
        mock_suite.status = "PASS"
        
        suite_stats.start_suite(mock_suite)
        
        self.assertEqual(suite_stats.total_suite, 1)
        self.assertEqual(suite_stats.passed_suite, 1)
        self.assertEqual(suite_stats.failed_suite, 0)
        self.assertEqual(suite_stats.skipped_suite, 0)

    def test_suite_stats_skipped_suite(self):
        """Test SuiteStats with skipped status"""
        suite_stats = SuiteStats()
        
        # Create a mock suite with SKIP status
        mock_suite = Mock()
        mock_suite.tests = [Mock()]  # Has tests
        mock_suite.status = "SKIP"
        
        suite_stats.start_suite(mock_suite)
        
        self.assertEqual(suite_stats.total_suite, 1)
        self.assertEqual(suite_stats.passed_suite, 0)
        self.assertEqual(suite_stats.failed_suite, 0)
        self.assertEqual(suite_stats.skipped_suite, 1)

    def test_suite_stats_failed_suite(self):
        """Test SuiteStats with failed status"""
        suite_stats = SuiteStats()
        
        # Create a mock suite with FAIL status
        mock_suite = Mock()
        mock_suite.tests = [Mock()]  # Has tests
        mock_suite.status = "FAIL"
        
        suite_stats.start_suite(mock_suite)
        
        self.assertEqual(suite_stats.total_suite, 1)
        self.assertEqual(suite_stats.passed_suite, 0)
        self.assertEqual(suite_stats.failed_suite, 1)
        self.assertEqual(suite_stats.skipped_suite, 0)

    def test_suite_stats_empty_suite(self):
        """Test SuiteStats with empty suite (no tests)"""
        suite_stats = SuiteStats()
        
        # Create a mock suite with no tests
        mock_suite = Mock()
        mock_suite.tests = []  # Empty test list
        mock_suite.status = "PASS"
        
        suite_stats.start_suite(mock_suite)
        
        # Should not count empty suites
        self.assertEqual(suite_stats.total_suite, 0)
        self.assertEqual(suite_stats.passed_suite, 0)
        self.assertEqual(suite_stats.failed_suite, 0)
        self.assertEqual(suite_stats.skipped_suite, 0)

    def test_suite_results_empty_suite(self):
        """Test SuiteResults with empty suite (no tests)"""
        mock_db = Mock()
        suite_results = SuiteResults(mock_db, "123", "False")
        
        # Create a mock suite with no tests
        mock_suite = Mock()
        mock_suite.tests = []  # Empty test list
        
        with patch("robotframework_historic_parser.rfhistoricparser.insert_into_suite_table") as mock_insert:
            suite_results.start_suite(mock_suite)
            # Should not insert empty suites
            mock_insert.assert_not_called()

    def test_suite_results_full_suite_name_true(self):
        """Test SuiteResults with full_suite_name=True"""
        mock_db = Mock()
        suite_results = SuiteResults(mock_db, "123", "True")
        
        # Create a mock suite with longname
        mock_suite = MagicMock()
        mock_suite.tests = [Mock()]  # Has tests
        mock_suite.longname = "MyProject.MySuite.MySubSuite"
        mock_suite.status = "PASS"
        
        # Create a simple object to hold statistics
        class Stats:
            total = 10
            passed = 5
            failed = 3
            skipped = 2
        
        mock_suite.statistics = Stats()
        mock_suite.elapsedtime = 120000  # 2 minutes in milliseconds
        
        with patch("robotframework_historic_parser.rfhistoricparser.insert_into_suite_table") as mock_insert:
            suite_results.start_suite(mock_suite)
            # Verify insert was called with the full suite name
            self.assertTrue(mock_insert.called)
            # Check that longname was used (first call, argument index 2 is the suite name)
            call_args = mock_insert.call_args[0]
            self.assertEqual(call_args[2], "MyProject.MySuite.MySubSuite")

    def test_suite_results_visit_test_full_suite_name_true(self):
        """Test TestMetrics.visit_test with full_suite_name=True"""
        from robotframework_historic_parser.rfhistoricparser import TestMetrics
        
        mock_db = Mock()
        test_results = TestMetrics(mock_db, "123", "True")
        
        # Create a mock test with longname
        mock_test = Mock()
        mock_test.name = "MyTest"
        mock_test.longname = "MyProject.MySuite.MyTest"
        mock_test.status = "PASS"
        mock_test.elapsedtime = 60000  # 1 minute in milliseconds
        mock_test.message = "Test passed"
        mock_test.tags = ["tag1", "tag2"]
        
        with patch("robotframework_historic_parser.rfhistoricparser.insert_into_test_table"):
            test_results.visit_test(mock_test)

    @patch("mysql.connector.connect")
    def test_insert_into_execution_table_full_coverage(self, mock_connect):
        """Test insert_into_execution_table with all database operations"""
        mock_con = Mock()
        mock_ocon = Mock()
        mock_cursor = Mock()
        mock_root_cursor = Mock()
        
        mock_con.cursor.return_value = mock_cursor
        mock_ocon.cursor.return_value = mock_root_cursor
        
        # Mock the fetchone results
        mock_cursor.fetchone.side_effect = [
            (1, 5, 10),  # Execution_Id, Execution_Pass, Execution_Total
            (100,)  # COUNT(*)
        ]
        
        result = insert_into_execution_table(
            mock_con, mock_ocon, "Test Execution", 10, 5, 3, "2.5", 
            20, 15, 3, 2, 0, "TestProject"
        )
        
        # Verify the execution ID is returned
        self.assertEqual(result, "1")
        
        # Verify cursor operations
        mock_cursor.execute.assert_called()
        mock_con.commit.assert_called_once()
        mock_root_cursor.execute.assert_called_once()
        mock_ocon.commit.assert_called_once()

    @patch("mysql.connector.connect")
    def test_insert_into_execution_table_zero_total(self, mock_connect):
        """Test insert_into_execution_table handles division by zero"""
        mock_con = Mock()
        mock_ocon = Mock()
        mock_cursor = Mock()
        mock_root_cursor = Mock()
        
        mock_con.cursor.return_value = mock_cursor
        mock_ocon.cursor.return_value = mock_root_cursor
        
        # Mock with zero total to test division by zero handling
        mock_cursor.fetchone.side_effect = [
            (1, 0, 0),  # Execution_Id, Execution_Pass=0, Execution_Total=0
            (100,)  # COUNT(*)
        ]
        
        result = insert_into_execution_table(
            mock_con, mock_ocon, "Test Execution", 0, 0, 0, "0", 
            0, 0, 0, 0, 0, "TestProject"
        )
        
        # Verify it doesn't crash and returns the execution ID
        self.assertEqual(result, "1")
        mock_con.commit.assert_called_once()
        mock_ocon.commit.assert_called_once()
