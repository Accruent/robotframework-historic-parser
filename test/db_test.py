"""Unit tests for functions using db in Robotframework Historic Parser"""
import unittest
from unittest.mock import patch, MagicMock, call

from robotframework_historic_parser.old_rfhistoricparser import connect_to_mysql_db


class TestDBFunctions(unittest.TestCase):
    """Unit Tests for db connection"""
    @patch('mysql.connector.connect')
    def test_connect_to_mysql_db(self, connect_mock):
        """Tests the mysql connection function"""
        connect_mock.return_value = MagicMock(name='connection_return')
        args = (1, 2, 3, 4, 5)
        connect_to_mysql_db(*args)
        self.assertEqual(1, connect_mock.call_count)
        self.assertEqual(connect_mock.call_args_list[0], call(host=args[0], port=args[1],
                                                              user=args[2], passwd=args[3],
                                                              database=args[4]))

    def test_connect_to_mysql_db_error(self):
        """Tests the mysql connection function when connection fails"""
        args = (1, 2, 3, 4, 5)
        connect_to_mysql_db(*args)
        self.assertRaises(AttributeError)
