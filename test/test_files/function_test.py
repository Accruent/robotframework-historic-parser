"""Unit tests for functions used in Robot Framework Historic Parser"""
import io
import sys
import unittest
from robotframework_historic_parser.parserargs import parse_options
from robotframework_historic_parser.rfhistoricparser import get_time_in_min, rfhistoric_parser


class TestFunctions(unittest.TestCase):
    """Unit Tests for functions"""

    def test_get_time_in_min(self):
        """This test verifies that get_time_in_min returns a time in minutes. """
        test_time = '01:02:03'
        expected_result = 62.05
        result_in_minutes = get_time_in_min(test_time)
        self.assertEqual(result_in_minutes, expected_result)

    def test_get_time_in_min_bad_input(self):
        """This test verifies that get_time_in_min returns error if invalid input is passed. """
        self.assertRaisesRegex(ValueError, 'not enough values to unpack', get_time_in_min, 'a')

    def test_rfhistoric_parser_ignore_result(self):
        """This test verifies that get_time_in_min returns a time in minutes. """
        captured_output = io.StringIO()
        sys.stdout = captured_output
        sys.argv[1:] = ['-g', 'True']
        test_opts = parse_options()
        rfhistoric_parser(test_opts)
        sys.stdout = sys.__stdout__
        result = captured_output.getvalue().strip()
        self.assertEqual(result, 'Ignoring execution results...')
