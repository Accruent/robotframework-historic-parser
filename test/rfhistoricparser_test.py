"""Unit tests for functions used in Robot Framework Historic Parser rfhistoricparser"""
import sys
import unittest
from unittest.mock import patch
from robotframework_historic_parser.rfhistoricparser import (
    get_time_in_min,
    rfhistoric_parser,
    remove_special_characters,
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
