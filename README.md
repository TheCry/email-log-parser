# email-log-parser
With this script, in cooperation with the Nagios plugin "check_log", you can search any log for certain words. As soon as the search term is found, the script sends an email to the recipient.

## Requirements
* python
* Nagios plugin "check_log" (Debian: monitoring-plugins-basic)

## How to use the script
* apt-get install git
* git clone https://github.com/TheCry/email-log-parser
* Set up the variables inside the script (vi emailLogParser.py)
* Make the file "emailLogParser.py" executable (chmod +x emailLogParser.py)
* Start the script to check whether it is working fine (./emailLogParser.py)

## No email after first run
When the script is executed for the first time, only the temporary file is created. Only after that the script takes effect with the search terms.

## Create a cron job
*/15 * * * * root nice -n 5 /path/emailLogParser.py >> /path/emailLogParser.log 2>&1