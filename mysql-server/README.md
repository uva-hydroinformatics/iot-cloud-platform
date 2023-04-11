# MySQL server
The python scripts in the 'python-data-ingestion' folders need to be copied to the MySQL database. The database creation commands are described in the mysql-database folder. To obtain the server credentials run the command "cat bitnami_credentials" in the home directory. 


# Initial setup

- Create MySQL database by executing commands listed in the mysql-database folder(replace ?????????? by username and password)
- Install python module dependencies
- create AWS config and credential files in "~/.aws/"
- Update database and TTN parameters in MySQL_parameters.py and TTN_parameters.py
- Configure the bash script MySQL_ingestion_scripts.sh to run at startup with crontab 

