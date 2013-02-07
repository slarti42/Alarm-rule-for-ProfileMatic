#!/usr/bin/python
# version 11
# author: slarti

import dbus, gobject
from datetime import datetime,timedelta
import subprocess

ses_bus = dbus.SessionBus()
pm_obj = ses_bus.get_object('org.ajalkane.profilematic', '/org/ajalkane/profilematic')
pm_intf = dbus.Interface(pm_obj, 'org.ajalkane.profilematic')
passwd = 'Test'

def split_rule_structure(rule_struct):
	rule_id = rule_struct[0]
	rule_name = rule_struct[1]
	active = rule_struct[2]
	smthng = rule_struct[3]
	rules_struct = rule_struct[4]
	actions_struct = rule_struct[5]
	list_of_rules = []

	for i in range(len(rules_struct)):
		list_of_rules.append(rule_struct[4][i])

	new_rule_struct = [rule_id,rule_name,active,smthng,list_of_rules,actions_struct]

	return new_rule_struct

def check_for_alarm_rule(timestamp):
	if pm_intf.getRuleIdForName('Alarm rule'):
		rule_id = pm_intf.getRuleIdForName('Alarm rule')
		print 'Alarm rule found, updating rule.'
		update_rule(timestamp,rule_id)
	else:
		alarm_rule_struct = dbus.Struct((dbus.String(u'{someruleid}'), dbus.String(u'Alarm rule'), dbus.Boolean(False), dbus.Boolean(False), dbus.Struct((dbus.Struct((dbus.Int32(0), dbus.Int32(0), dbus.Int32(0), dbus.Int32(0)), signature=None), dbus.Struct((dbus.Int32(0), dbus.Int32(0), dbus.Int32(0), dbus.Int32(0)), signature=None), dbus.Array([dbus.Int32(0)], signature=dbus.Signature('i')), dbus.Array([], signature=dbus.Signature('i')), dbus.Int32(0), dbus.Array([], signature=dbus.Signature('s')), dbus.Int32(0), dbus.Int32(-1), dbus.Struct((dbus.Array([], signature=dbus.Signature('ay')), dbus.Boolean(False)), signature=None), dbus.Int32(0), dbus.Int32(-1), dbus.Struct((dbus.Int32(-1), dbus.Int32(-1)), signature=None), dbus.Struct((dbus.String(u''), dbus.String(u''), dbus.Int32(0), dbus.Int32(0)), signature=None)), signature=None), dbus.Struct((dbus.String(u''), dbus.Boolean(False), dbus.Int32(-1), dbus.Int32(-1), dbus.Boolean(False), dbus.Int32(-1), dbus.Boolean(False), dbus.Int32(-1), dbus.Boolean(False), dbus.Int32(-1), dbus.Boolean(False), dbus.Int32(-1), dbus.Boolean(False), dbus.Int32(-1), dbus.Boolean(False), dbus.String(u'Erase this and edit rules and actions as you wish'), dbus.String(u''), dbus.Array([], signature=dbus.Signature('(usis)')), dbus.String(u''), dbus.Boolean(False), dbus.Int32(0), dbus.Struct((dbus.Array([], signature=dbus.Signature('s')),), signature=None)), signature=None)), signature=None)
		rule_id = pm_intf.appendRule(alarm_rule_struct)
		print 'No alarm rule. Appended rule.'
		update_rule(timestamp,rule_id)
		

def update_rule(timestamp,rule_id):
	if timestamp == 0:
		active = False
		start_h = 0
		start_min = 0
		stop_h = 0
		stop_min = 0
		weekday = 0
	else:
		dt_start = datetime.fromtimestamp(timestamp)
		dt_stop = dt_start + timedelta(minutes=1)
		active = True
		start_h = int(dt_start.strftime("%H"))
		start_min = int(dt_start.strftime("%M"))
		stop_h = int(dt_stop.strftime("%H"))
		stop_min = int(dt_stop.strftime("%M"))
		weekday = int(str(int(dt_start.strftime("%w"))-1).replace("-1","6"))
	all_rules = pm_intf.getRules()
	alarm_rule_index = [i[1] for i in all_rules].index('Alarm rule')
	rule_struct = split_rule_structure(all_rules[alarm_rule_index])	
	rule_struct[0] = rule_id
	rule_struct[2] = active
	rule_struct[4][0] = [start_h,start_min,0,0]
	rule_struct[4][1] = [stop_h,stop_min,0,0]
	rule_struct[4][2] = [weekday]
	print active,start_h,start_min,stop_h,stop_min,weekday
	pm_intf.updateRule(rule_struct)

from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
sys_bus = dbus.SystemBus()

def process_signal(received_signal):
	alarm_obj = sys_bus.get_object('com.nokia.time', '/org/maemo/contextkit/Alarm/Trigger')
	alarms_dict = alarm_obj.Get(dbus_interface='org.maemo.contextkit.Property')[0][0]
	time_obj = sys_bus.get_object('com.nokia.time', '/com/nokia/time')
	time_intf = dbus.Interface(time_obj, 'com.nokia.time')
	inverse_alarms_dict = {}
	cookies = alarms_dict.keys()
	for cookie in cookies:
		timestamp = alarms_dict[cookie]
		attributes = time_intf.query_attributes(cookie)
		inverse_alarms_dict.update({timestamp:attributes})
	
	if received_signal == 1:
		print 'Alarm went off. Doing nothing.'
	elif received_signal == 0:
		print 'No alarms. Passed zero.'
		check_for_alarm_rule(received_signal)
		subprocess.Popen("qdbus com.meego.core.MNotificationManager /notificationmanager com.meego.core.MNotificationManager.addNotification 0 0 'device' '' 'No alarms. Alarm rule disabled.' '' '/usr/share/icons/hicolor/80x80/apps/profilematic80.png' 0", shell=True)
	else:
		if inverse_alarms_dict[(received_signal*1000000000)]['TITLE'] == passwd:
			print 'Alarm with passwd found. Passed timestamp.'
			check_for_alarm_rule(received_signal)
			subprocess.Popen("qdbus com.meego.core.MNotificationManager /notificationmanager com.meego.core.MNotificationManager.addNotification 0 0 'device' '' 'Next alarm has correct title. Alarm rule activated.' '' '/usr/share/icons/hicolor/80x80/apps/profilematic80.png' 0", shell=True)
		else:
			print 'Alarm found with wrong passwd. Passed zero to disable.'
			check_for_alarm_rule(0)
			subprocess.Popen("qdbus com.meego.core.MNotificationManager /notificationmanager com.meego.core.MNotificationManager.addNotification 0 0 'device' '' 'Next alarm has wrong title. Alarm rule disabled.' '' '/usr/share/icons/hicolor/80x80/apps/profilematic80.png' 0", shell=True)

sys_bus.add_signal_receiver(process_signal,signal_name="next_bootup_event",dbus_interface="com.nokia.time")

loop = gobject.MainLoop()
loop.run()
