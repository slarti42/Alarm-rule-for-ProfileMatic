Alarm-rule-for-ProfileMatic
===========================

A python script that runs in the background listening for the next_bootup_event signal on the session bus of harmattan. It creates or updates a special alarm rule in ProfileMatic according to set or unset alarms with a certain title. The default title is 'Test' which is the value of the variable passwd.