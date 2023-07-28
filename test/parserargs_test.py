"""Unit tests for functions used in Robot Framework Historic Parser parserargs"""
import sys
import unittest
from unittest.mock import patch

from robotframework_historic_parser.parserargs import parse_options, main


class TestRunner(unittest.TestCase):
    """Unit Tests for parserargs.py"""

    def test_host(self):
        """Argument parser positive test for host"""
        sys.argv[1:] = ['-s', 'localhost']
        options = parse_options()
        self.assertEqual('localhost', options.host)

    def test_host_empty(self):
        """Argument parser negative test for host"""
        sys.argv[1:] = ['-s']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_port(self):
        """Argument parser positive test for port"""
        sys.argv[1:] = ['-t', '5000']
        options = parse_options()
        self.assertEqual('5000', options.port)

    def test_port_empty(self):
        """Argument parser negative test for port"""
        sys.argv[1:] = ['-t']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_user(self):
        """Argument parser positive test for user"""
        sys.argv[1:] = ['-u', 'username']
        options = parse_options()
        self.assertEqual('username', options.username)

    def test_user_empty(self):
        """Argument parser negative test for user"""
        sys.argv[1:] = ['-u']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_pass(self):
        """Argument parser positive test for pass"""
        sys.argv[1:] = ['-p', 'password']
        options = parse_options()
        self.assertEqual('password', options.password)

    def test_pass_empty(self):
        """Argument parser negative test for pass"""
        sys.argv[1:] = ['-p']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_project(self):
        """Argument parser positive test for project"""
        sys.argv[1:] = ['-n', 'test_project']
        options = parse_options()
        self.assertEqual('test_project', options.projectname)

    def test_project_empty(self):
        """Argument parser negative test for project"""
        sys.argv[1:] = ['-n']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_execution(self):
        """Argument parser positive test for execution"""
        sys.argv[1:] = ['-e', 'QA_TEST']
        options = parse_options()
        self.assertEqual('QA_TEST', options.executionname)

    def test_execution_empty(self):
        """Argument parser negative test for execution"""
        sys.argv[1:] = ['-e']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_path(self):
        """Argument parser positive test for path"""
        sys.argv[1:] = ['-i', '/temp/']
        options = parse_options()
        self.assertEqual('/temp/', options.path)

    def test_path_empty(self):
        """Argument parser negative test for path"""
        sys.argv[1:] = ['-i']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_output(self):
        """Argument parser positive test for output"""
        sys.argv[1:] = ['-o', 'test.xml']
        options = parse_options()
        self.assertEqual('test.xml', options.output)

    def test_output_empty(self):
        """Argument parser negative test for output"""
        sys.argv[1:] = ['-o']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_ignoreresult(self):
        """Argument parser positive test for ignoreresult"""
        sys.argv[1:] = ['-g', 'True']
        options = parse_options()
        self.assertEqual('True', options.ignoreresult)

    def test_ignoreresult_empty(self):
        """Argument parser negative test for ignoreresult"""
        sys.argv[1:] = ['-g']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_report_type(self):
        """Argument parser positive test for report_type"""
        sys.argv[1:] = ['--report_type', 'Allure']
        options = parse_options()
        self.assertEqual('Allure', options.ignoreresult)

    def test_report_type_empty(self):
        """Argument parser negative test for report_type"""
        sys.argv[1:] = ['--report_type']
        with self.assertRaises(SystemExit):
            parse_options()

    def test_fullsuitename(self):
        """Argument parser positive test for fullsuitename"""
        sys.argv[1:] = ['-f', 'True']
        options = parse_options()
        self.assertEqual('True', options.fullsuitename)

    def test_fullsuitename_empty(self):
        """Argument parser negative test for fullsuitename"""
        sys.argv[1:] = ['-f']
        with self.assertRaises(SystemExit):
            parse_options()

    @patch('robotframework_historic_parser.parserargs.rfhistoric_parser')
    # pylint: disable=R0201
    def test_main(self, pzf_mock):
        """Tests main function"""
        sys.argv[1:] = ['-f', 'test_files/testReport.html']
        main()
        pzf_mock.assert_called()
