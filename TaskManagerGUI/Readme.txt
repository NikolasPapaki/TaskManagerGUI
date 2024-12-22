In order for app to work.

1. Install python 
2. Run `pip install -r requirements.txt`
3. Create a shortcut of main.pyw
4. There is a known bug that happens when GUI is in the laptop screen and it turns transparent (Seem's it doesn't like 4k displays :\ )



How to configure your Tasks in Health Check:
- In the 'Health Check Manager' tab right click and select 'Add new healthcheck procedure'
- Give an appropriate name
- In the users if you want multiple users add them separated with a coma i.e "TCTCD1,TCTCD2"
- 'Only Local' switch ensures that that option will only be shown if a local environment is selected in the dropdown of "Health Check" frame
- 'Run as sysdba' switch will connect to database as sysdba if enabled
- 'Use Oracle Client' switch will make the use of oracle client to connect similar to 'sqlplus / as sysdba' in the command line.
    - No use to set 'Run as sysdba' switch for these types of procedures as sysdba is the default mode used