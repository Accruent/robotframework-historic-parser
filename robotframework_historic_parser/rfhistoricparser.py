"""Tool for parsing robot framework output.xl files."""
import os
import re
import json
import datetime
import mysql.connector
from robot.api import ExecutionResult, ResultVisitor
import xml.etree.ElementTree as ET


def rfhistoric_parser(opts):
    """Main parsing function."""
    if opts.ignoreresult == "True":
        print("Ignoring execution results...")
        return

    path = os.path.abspath(os.path.expanduser(opts.path))

    output_names = []
    # support "*.xml" and "*.json" output files
    if opts.output in ["*.xml", "*.json"]:
        for item in os.listdir(path):
            if os.path.isfile(item) and (item.endswith('.xml') or item.endswith('.json')):
                output_names.append(item)
    else:
        for curr_name in opts.output.split(","):
            curr_path = os.path.join(path, curr_name)
            output_names.append(curr_path)

    required_files = list(output_names)
    missing_files = [filename for filename in required_files if not os.path.exists(filename)]
    if missing_files:
        # We have files missing.
        exit("output.xml file is missing: {}".format(", ".join(missing_files)))

    if opts.report_type == "RF":
        # connect to database
        mydb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, opts.projectname)
        rootdb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, 'robothistoric')

        # Read output.xml file
        result = ExecutionResult(*output_names)
        result.configure(stat_config={'suite_stat_level': 2,
                                      'tag_stat_combine': 'tagANDanother'})

        print("Capturing execution results, This may take few minutes...")

        test_stats = SuiteStats()
        result.visit(test_stats)

        test_stats_obj = test_stats.all if hasattr(test_stats, 'all') else test_stats
        stotal = test_stats_obj.total_suite
        spass = test_stats_obj.passed_suite
        sfail = test_stats_obj.failed_suite
        sskip = test_stats_obj.skipped_suite if hasattr(test_stats_obj, 'skipped_suite') else 0


        stats = result.statistics
        stats_obj = stats.total.all if hasattr(stats.total, 'all') else stats.total
        total = stats_obj.total
        passed = stats_obj.passed
        failed = stats_obj.failed
        skipped = stats_obj.skipped if hasattr(stats_obj, 'skipped') else 0

        elapsedtime = datetime.datetime(1970, 1, 1) + \
            datetime.timedelta(milliseconds=result.suite.elapsedtime)
        elapsedtime = get_time_in_min(elapsedtime.strftime("%X"))
        elapsedtime = float("{0:.2f}".format(elapsedtime))

        # insert test results info into db
        result_id = insert_into_execution_table(mydb, rootdb, opts.executionname, total, passed,
                                                failed, elapsedtime, stotal, spass, sfail, skipped,
                                                sskip, opts.projectname)

        print("INFO: Capturing suite results")
        result.visit(SuiteResults(mydb, result_id, opts.fullsuitename))
        print("INFO: Capturing test results")
        result.visit(TestMetrics(mydb, result_id, opts.fullsuitename))

        print("INFO: Writing execution results")
        commit_and_close_db(mydb)

    elif opts.report_type.lower() == "allure":
        process_allure_report(opts)
    elif opts.report_type.lower() == "junit":
        process_junit_report(opts)
    elif opts.report_type.lower() == "statistics":
        process_statistics_report(opts)
    else:
        exit(f"report_type of {opts.report_type} is not supported.")


# other useful methods
class SuiteStats(ResultVisitor):
    """Method for parsing Suite Stats"""
    total_suite = 0
    passed_suite = 0
    failed_suite = 0
    skipped_suite = 0

    def start_suite(self, suite):
        suite_test_list = suite.tests
        if not suite_test_list:
            pass
        else:
            self.total_suite += 1

            if suite.status == "PASS":
                self.passed_suite += 1
            elif suite.status == "FAIL":
                self.failed_suite += 1
            else:
                self.skipped_suite += 1


class SuiteResults(ResultVisitor):
    """Method for parsing Suite Results"""

    def __init__(self, db, id, full_suite_name):
        self.db = db
        self.id = id
        self.full_suite_name = full_suite_name

    def start_suite(self, suite):

        suite_test_list = suite.tests
        if not suite_test_list:
            pass
        else:
            if self.full_suite_name == "True":
                suite_name = suite.longname
            else:
                suite_name = suite

            stats = suite.statistics.all if hasattr(suite.statistics, 'all') else suite.statistics
            time = float("{0:.2f}".format(suite.elapsedtime / float(60000)))
            suite_skipped = stats.skipped if hasattr(stats, 'skipped') else 0
            insert_into_suite_table(self.db, self.id, str(suite_name), str(suite.status),
                                    int(stats.total), int(stats.passed), int(stats.failed),
                                    float(time), int(suite_skipped))


class TestMetrics(ResultVisitor):
    """Method for parsing Suite Metrics"""

    def __init__(self, db, id, full_suite_name):
        self.db = db
        self.id = id
        self.full_suite_name = full_suite_name

    def visit_test(self, test):
        if self.full_suite_name == "True":
            full_suite_name = test.longname.split("." + test.name)
            name = str(full_suite_name[0]) + " - " + str(test)
        else:
            name = str(test.parent) + " - " + str(test)

        time = float("{0:.2f}".format(test.elapsedtime / float(60000)))
        error = remove_special_characters(str(test.message))
        insert_into_test_table(self.db, self.id, str(name), str(test.status), time, error,
                               str(test.tags))


def get_time_in_min(time_str):
    """Method converting time to minutes"""
    h, m, s = time_str.split(':')
    ctime = int(h) * 3600 + int(m) * 60 + int(s)
    return float("{0:.2f}".format(ctime / 60))


def connect_to_mysql_db(host, port, user, pwd, db):
    """Method for connection to db"""
    try:
        mydb = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            passwd=pwd,
            database=db
        )
        return mydb
    except Exception as e:
        print(e)


def insert_into_execution_table(con, ocon, name, total, passed, failed, ctime, stotal, spass,
                                sfail, skipped, sskipped, projectname):
    """Method for inserting parsed data into tb_execution"""
    cursor_obj = con.cursor()
    root_cursor_obj = ocon.cursor()
    utc = datetime.datetime.utcnow()
    sql = "INSERT INTO TB_EXECUTION (Execution_Id, Execution_Date, Execution_Desc, " \
          "Execution_Total, Execution_Pass, Execution_Fail, Execution_Time, Execution_STotal, " \
          "Execution_SPass, Execution_SFail, Execution_Skip, Execution_SSkip) VALUES (0, %s, " \
          "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    val = (utc, name, total, passed, failed, ctime, stotal, spass, sfail, skipped, sskipped)
    cursor_obj.execute(sql, val)
    con.commit()
    cursor_obj.execute(
        "SELECT Execution_Id, Execution_Pass, Execution_Total FROM TB_EXECUTION ORDER BY "
        "Execution_Id DESC LIMIT 1;")
    rows = cursor_obj.fetchone()
    cursor_obj.execute("SELECT COUNT(*) FROM TB_EXECUTION;")
    execution_rows = cursor_obj.fetchone()
    # update robothistoric.TB_PROJECT table
    root_cursor_obj.execute(
        "UPDATE TB_PROJECT SET Last_Updated = '%s', Total_Executions = %s, Recent_Pass_Perc = %s "
        "WHERE Project_Name='%s';" % (utc, execution_rows[0],
                                      float("{0:.2f}".format((rows[1] / rows[2] * 100))) if rows[2] != 0 else 0,
                                      projectname))
    ocon.commit()
    return str(rows[0])


def insert_into_suite_table(con, eid, name, status, total, passed, failed, duration, skipped):
    """Method for inserting parsed data into tb_suite"""
    cursor_obj = con.cursor()
    sql = "INSERT INTO TB_SUITE (Suite_Id, Execution_Id, Suite_Name, Suite_Status, Suite_Total, " \
          "Suite_Pass, Suite_Fail, Suite_Time, Suite_Skip) VALUES (%s, %s, %s, %s, %s, %s, %s, " \
          "%s, %s)"
    val = (0, eid, name, status, total, passed, failed, duration, skipped)
    cursor_obj.execute(sql, val)


def insert_into_test_table(con, eid, test, status, duration, msg, tags):
    """Method for inserting parsed data into tb_test"""
    cursor_obj = con.cursor()
    sql = "INSERT INTO TB_TEST (Test_Id, Execution_Id, Test_Name, Test_Status, Test_Time, " \
          "Test_Error, Test_Tag) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (0, eid, test, status, duration, msg, tags)
    cursor_obj.execute(sql, val)


def commit_and_close_db(db):
    """Method for closing the db"""
    db.commit()
    db.close()


# Allure Report Functions
def process_allure_report(opts):
    mydb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, opts.projectname)
    rootdb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, 'robothistoric')

    total = 0
    passed = 0
    failed = 0
    skipped = 0
    elapsedtime = 0
    # Retrieving suite data is currently not implemented
    stotal = 0
    spass = 0
    sfail = 0
    sskip = 0

    if opts.output.endswith('.xml'):
        root = ET.parse(opts.output).getroot()

        total = root.get('total', '0')
        passed = root.get('passed', '0')
        failed = int(root.get('failed', '0')) + int(root.get('inconclusive', '0'))
        skipped = root.get('skipped', '0')
        elapsedtime = root.get('duration', '0')

    # if this is in a summary.json
    elif opts.output.endswith('.json'):
        with open(opts.output, 'r') as f:
            data = json.load(f)

        # Navigate to 'statistic' key
        statistics = data.get('statistic', {})

        total = statistics.get('total', '0')
        passed = statistics.get('passed', '0')
        failed = int(statistics.get('failed', '0')) + int(statistics.get('unknown', '0'))
        skipped = statistics.get('skipped', '0')
        elapsedtime = '0' # duration data not saved in the summary.json
    else:
        print("Invalid file type. Please provide either .xml or .json file.")

    # insert test results info into db
    insert_into_execution_table(mydb, rootdb, opts.executionname, total, passed, failed, elapsedtime, stotal, spass,
                                sfail, skipped, sskip, opts.projectname)

    print("INFO: Writing execution results")
    mydb.close()


# JUnit Report Functions
def process_junit_report(opts):
    mydb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, opts.projectname)
    rootdb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, 'robothistoric')

    # Retrieving suite data is currently not implemented
    stotal = 0
    spass = 0
    sfail = 0
    sskip = 0

    root = ET.parse(opts.output).getroot()
    testsuite = root.find('testsuite')

    total = int(testsuite.get('tests', '0'))
    failed = int(testsuite.get('failures', '0')) + int(testsuite.get('errors', '0'))
    skipped = int(testsuite.get('skipped', '0'))
    passed = total - failed - skipped
    elapsedtime = float(testsuite.get('time', '0'))


    # insert test results info into db
    insert_into_execution_table(mydb, rootdb, opts.executionname, total, passed, failed, elapsedtime, stotal, spass,
                                sfail, skipped, sskip, opts.projectname)

    print("INFO: Writing execution results")
    mydb.close()


def process_statistics_report(opts):
    mydb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, opts.projectname)
    rootdb = connect_to_mysql_db(opts.host, opts.port, opts.username, opts.password, 'robothistoric')

    # Initialize counts
    passed_count = 0
    failed_count = 0
    skipped_count = 0
    total_count = 0

    if opts.output.endswith('.json'):
        with open(opts.output, 'r') as f:
            data = json.load(f)

            # Iterate over properties and extract relevant counts
            for prop in data.get('property', []):
                if prop['name'] == 'PassedTestCount':
                    passed_count = int(prop['value'])
                elif prop['name'] == 'FailedTestCount':
                    failed_count = int(prop['value'])
                elif prop['name'] == 'SkippedTestCount':
                    skipped_count = int(prop['value'])
                elif prop['name'] == 'TotalTestCount':
                    total_count = int(prop['value'])

    else:
        print("Invalid file type. Please provide a .json file.")
        return

    # insert test results info into db (adjust this part as needed)
    insert_into_execution_table(mydb, rootdb, opts.executionname, total_count, passed_count, failed_count, 0, 0, 0, 0, skipped_count, 0, opts.projectname)

    print("INFO: Writing statistics results")
    mydb.close()


def remove_special_characters(string):
    return re.sub(r'[^a-zA-Z0-9 ]', '', string)
