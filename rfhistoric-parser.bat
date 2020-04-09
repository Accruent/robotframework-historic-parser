@echo off

rfhistoricparser -o "%WORKSPACE%/output/output.xml" -s "hostip" -t 3306 -u "username" -p "password" -n "%1" -e "%2"