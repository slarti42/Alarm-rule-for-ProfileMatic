Alarm-rule-for-ProfileMatic
===========================

A python script that runs in the background listening for the next_bootup_event signal on the system bus of harmattan. It creates or updates a special alarm rule in ProfileMatic according to set or unset alarms with a certain title. The default title is 'Test' which is the value of the variable passwd. This version works with ProfileMatic 2.0 but will work with older versions if you create a rule named 'Alarm rule' before starting the script. To make this run automatically on startup, add the script to the default rule as custom action.
