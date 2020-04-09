# Tools
Repository for random scripts I write

create_table.py
---------------
A script to convert a CSV to Jira/Confluence table markdown. 

usage: 

convert_table.py input.csv output.txt

patch_tuesday_sec_updates.py
---------------
This script pulls the Microsoft patch Tuesday Security updates for the current month and submits a Jira Issue with a .csv of the data. The contents are also displayed in the description field using Jira's Table markdown.

usage: 

I currently have this configured to run via cron every day at 4pm. If the date it runs equals the second tuesday of the month, it will automatically submit the jira ticket containing the security updates for the current month.

vpn.sh
---------------
Randomly selects a config file from a list of vpn configs, verifies there is not currently a tunnel set up, then spawns the openvpn process and enters your username/password.
