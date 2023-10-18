import os
import argparse
from .rfhistoricparser import rfhistoric_parser


def parse_options():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    general = parser.add_argument_group("Parser")

    general.add_argument(
        '-s', '--host',
        dest='host',
        default='localhost',
        help="MySQL hosted address"
    )

    general.add_argument(
        '-t', '--port',
        dest='port',
        default=3306,
        help="MySQL port"
    )

    general.add_argument(
        '-u', '--username',
        dest='username',
        default='superuser',
        help="MySQL db user name"
    )

    general.add_argument(
        '-p', '--password',
        dest='password',
        default='passw0rd',
        help="MySQL db password"
    )

    general.add_argument(
        '-n', '--projectname',
        dest='projectname',
        help="Name of the project"
    )

    general.add_argument(
        '-e', '--executionname',
        dest='executionname',
        help="Name of the execution"
    )

    general.add_argument(
        '-i', '--inputpath',
        dest='path',
        default=os.path.curdir,
        help="Path of result files"
    )

    general.add_argument(
        '-o', '--output',
        dest='output',
        default="output.xml",
        help="Name of output.xml"
    )

    general.add_argument(
        '-g', '--ignoreresult',
        dest='ignoreresult',
        default="False",
        help="Flag to ignore execution result, by this flag we can restrict storing results into mysql"
    )

    general.add_argument(
        '-f', '--fullsuitename',
        dest='fullsuitename',
        default="False",
        help="Use full suite name"
    )

    general.add_argument(
        '--report_type',
        dest='report_type',
        default="RF",
        help="Sets the report type to import, defaults to RF. Other options: Allure, JUnit"
    )

    return parser.parse_args()


def main():
    args = parse_options()
    rfhistoric_parser(args)
