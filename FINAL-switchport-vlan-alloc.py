#!/usr/bin/python

# The below script performs switchport vlan change 
# on Cisco IOS, IOS-XE and NXOS devices only

# Only vlans of switch ports with mode access are changed
# Trunk and routed interface vlan assignments are changed 
# only if tose ports are down


# Base file Created on: 18th May 2020
# Updated on: 3rd April 2021

# Version-1: The version 1 included addition of checks for Cisco IOS 
# Version-2: The version 2 included calling of functions and also	
#    		 switch Cisco IOS or NXOS identification
# Version-3: The version 3 included nxos port checks for transciever sbsent, 
#            port not connnected, ntc template required steps inclusion
# Version-4: The version 4 returned the value of the switch port config 
#            and also the switchport config is updated. 
#            Added check for trunk and routed ports with down status
# Version-5: The version 5 was created to find the down ports time
# Version-6: The version 6 was created to filter on the show interface list 
#			 for the nxos, ios, ios-xe code types
# version-7: The version 7 was created to modify the code workflow to 
#            include checks and command captures of ios, ios-xe, nxos ios types
# version-8: The version 8 was created to include module to check if 
#            switch responds to telnet or ssh
# version-9: The version 9 was created to include voice vlan and spanning tree portfast commands
#			 in the switchport configuration
# version-10: The version 10 was created to include dscription command
#			 in the switchport configuration
# version-11: The version 11 was created to include the command execution block
# version-12: The version 12 was created to capture all the logs in a log file


# Script Pre-requisites to run:
# 1. Install netmiko and paramiko module 
# 2. Install netaddr module
# 3. Install ipaddr module
# 4. Define the NET_TEXTFSM= path
#    For Windows/Linux/MacOS: https://www.schrodinger.com/kb/1842
#    For Linux: https://pynet.twb-tech.com/blog/automation/netmiko-textfsm.html
#    you should also edit the ntc template cisco_ios_show_interfaces_status.textfsm to include the NXOS notconnec & xcvrAbsen interface status to match



import textfsm
import getpass
import sys
import os
import socket
import shutil
import telnetlib
import time
from datetime import datetime
import socket
import paramiko
import netmiko
import netaddr
from netaddr import *
from netmiko import ConnectHandler
import ipaddress
import logging
import ftplib
import smtplib
from socket import gaierror
import csv



script_log = "" # Used to store the script logs
log_file_datestr = "" # Used to store the date for script log filename
username = ' '
password = ' '

log_file_datestr = time.strftime("_%d_%m_%Y_%H_%M_%S")




# Function definition  
def myfunc(switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password):

# Defining Variables to track up, down, and err disable ports
	portdown = ''
	portup = ''
	porterr = ''
	
	portdown_count = 0
	portup_count = 0
	porterr_count = 0
	myfunc_log = "" # Used to store the myfunc function logs

	myfunc_log = myfunc_log + "\n\n\n\n"
	myfunc_log = myfunc_log + "\n**************************************************************"
	myfunc_log = myfunc_log + "\n        The start of the myfunc funtion call"
	myfunc_log = myfunc_log + "\n**************************************************************"

	print("\n\n\n\n")
	
	myfunc_log = myfunc_log + "\n\nChecking if switch code is IOS, IOS-XE or NXOS"
	myfunc_log = myfunc_log + "\nto find the key value used to find the last interface flap"
	
	if ios_type == "IOS" or ios_type == "IOS-XE":
		last_link_flapped = "last_input"
		print("\nThe IOS type is: " + str(ios_type) + " and the last link flapped variable value is: " + str(last_link_flapped))
		myfunc_log = myfunc_log + "\nThe IOS type is: " + str(ios_type) + " and the last link flapped variable value is: " + str(last_link_flapped)
		#time.sleep(3)
		
		if sshchk == 1:
	# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_ios',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '22',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for SSH")
			myfunc_log = myfunc_log + "\n\nThe connection handler is set for SSH with in the myfunc function since the switch responded to SSH socket check."
			#time.sleep(5)
		elif telnetchk == 1:
			# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_ios_telnet',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '23',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for TELNET")
			myfunc_log = myfunc_log + "\n\nThe connection handler is set for TELNET with in the myfunc function since the switch responded to TELNET socket check."
			#time.sleep(5)
	

		try:

# The defined connection handler connects to the IOS switch
			myfunc_log = myfunc_log + "\nTrying to connect to switch using Netmiko connection handler within the myfunc function."
			print("\nTrying to connect to switch using Netmiko connection handler within the myfunc function.")
			net_connect = ConnectHandler(**switch_cisco_ios)
			#net_connect.find_prompt()

# If the command execution fails then execute the exception block of commands			
			net_connect.enable()
			myfunc_log = myfunc_log + "\nSuccessfully connected to the switch."
			
# Get the output of the show ver command
			sh_ver = net_connect.send_command('show version', cmd_verify=False)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show version command."
			
# Get the output of the show int status command
			sh_int_status = net_connect.send_command('show int status', cmd_verify=False, use_textfsm=True)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show int status command."
			
# Get the output of the show interface command
			sh_intf = net_connect.send_command('show interface', cmd_verify=False, use_textfsm=True)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show interface command."
			#print("\n\n" + str(sh_intf))
			#time.sleep(500)
			
# Get the output of the show vlan command
			sh_vlan = net_connect.send_command('show vlan', cmd_verify=False, use_textfsm=True)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show vlan command."

# Close the ssh session of the device
			net_connect.disconnect()
			myfunc_log = myfunc_log + "\nDisconnected from the switch."
		
		except:
			print ("The session could not be established with the switch.")
			print ("Please ensure the ip address or the switch name is correct and you are conecting to a switch and not a router.")
			print ("or the Switch name should have a correct DNS entry.")
			myfunc_log = myfunc_log + "\n\nThe session could not be established with the switch."
			myfunc_log = myfunc_log + "\nPlease ensure the ip address or the switch name is correct and you are conecting to a switch and not a router."
			myfunc_log = myfunc_log + "\nor the Switch name should have a correct DNS entry."
	
	elif ios_type == "NXOS":
		last_link_flapped = "last_link_flapped"	
		print("\nThe IOS type is: " + str(ios_type) + " and the last link flapped variable value is: " + str(last_link_flapped))
		myfunc_log = myfunc_log + "\nThe IOS type is: " + str(ios_type) + " and the last link flapped variable value is: " + str(last_link_flapped)
		#time.sleep(3)		


		if sshchk == 1:
	# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_nxos',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '22',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for SSH")
			myfunc_log = myfunc_log + "\n\nThe connection handler is set for SSH with in the myfunc function since the switch responded to SSH socket check."
			#time.sleep(5)
		elif telnetchk == 1:
			# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_nxos_telnet',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '23',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for TELNET")
			myfunc_log = myfunc_log + "\n\nThe connection handler is set for TELNET with in the myfunc function since the switch responded to TELNET socket check."
			#time.sleep(5)
			

		try:

# The defined connection handler connects to the IOS switch
			myfunc_log = myfunc_log + "\nTrying to connect to switch using Netmiko connection handler within the myfunc function."
			print("\nTrying to connect to switch using Netmiko connection handler within the myfunc function.")
			net_connect = ConnectHandler(**switch_cisco_ios)
			#net_connect.find_prompt()

# If the command execution fails then execute the exception block of commands			
			net_connect.enable()
			myfunc_log = myfunc_log + "\nSuccessfully connected to the switch."
			
# Get the output of the show ver command
			sh_ver = net_connect.send_command('show version', cmd_verify=False)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show version command."
			
# Get the output of the show int status command
			sh_int_status = net_connect.send_command('show int status', cmd_verify=False, use_textfsm=True)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show int status command."
			
# Get the output of the show interface command
			sh_intf = net_connect.send_command('show interface', cmd_verify=False, use_textfsm=True)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show interface command."
			#print("\n\n" + str(sh_intf))
			#time.sleep(500)
			
# Get the output of the show vlan command
			sh_vlan = net_connect.send_command('show vlan', cmd_verify=False, use_textfsm=True)
			myfunc_log = myfunc_log + "\nSuccessfully captured the show vlan command."
			
# Close the ssh session of the device
			net_connect.disconnect()
			myfunc_log = myfunc_log + "\nDisconnected from the switch."
		
		except:
			print ("The session could not be established with the switch.")
			print ("Please ensure the ip address or the switch name is correct and you are conecting to a switch and not a router.")
			print ("Switch name should have a correct DNS entry.")
			myfunc_log = myfunc_log + "\n\nThe session could not be established with the switch."
			myfunc_log = myfunc_log + "\nPlease ensure the ip address or the switch name is correct and you are conecting to a switch and not a router."
			myfunc_log = myfunc_log + "\nor the Switch name should have a correct DNS entry."



# Printing the number of interfaces and vlans	
	print("\n\nThe switch has " + str(len(sh_int_status)) + " interfaces.")
	numofinterfaces = len(sh_int_status)
	numofvlan = int(len(sh_vlan))
	print("\n\nThe switch has " + str(len(sh_vlan)) + " vlans.")	
	myfunc_log = myfunc_log + "\n\nThe switch has "  + str(len(sh_int_status)) + " interfaces."
	myfunc_log = myfunc_log + "\nThe switch has "  + str(len(sh_vlan)) + " vlans."
	
	
# Printing the list of vlans in the switch
	print('\n\nThe VLANS in the switch are: \n')
	myfunc_log = myfunc_log + "\n\nThe VLANS in the switch are: \n"
	for i in range(0, numofvlan):
		print(str(sh_vlan[i]['vlan_id']) + "    " + str(sh_vlan[i]['name']))
		myfunc_log = myfunc_log + "\n" + sh_vlan[i]['vlan_id'] + "    " + sh_vlan[i]['name']


# Printing the number of interfaces, their status, vlans allowed and last link flap value
	for i in range(0, numofinterfaces):
		port = sh_int_status[i]['port'].rstrip()
		status = sh_int_status[i]['status'].rstrip()
		vlan = sh_int_status[i]['vlan'].rstrip()

		last_input = sh_intf[i][str(last_link_flapped)].rstrip()

		#time.sleep(5)
		
		if status == 'notconnect' or status == 'notconnec' or status == 'disabled' or status == 'xcvrAbsen' or status == 'inactive' or status == 'down':
			portdown = portdown + str(port) + '    ' + str(status) + '    ' + str(vlan) + '    ' + str(last_input) +  '\n'
			portdown_count = portdown_count + 1
			#print("\n\n PortDOWN value is: " + str(portdown))
			#time.sleep(1)
		elif status == 'connected':
			portup = portup + str(port) + '    ' + str(status) + '    ' + str(vlan) + '    ' + str(last_input) + '\n'
			portup_count = portup_count + 1
			#print("\n\n PortUP value is: " + str(portup))
			#time.sleep(1)
		else:
			porterr = porterr + str(port) + '    ' + str(status) + '    ' + str(vlan) + '    ' + str(last_input) + '\n'
			porterr_count = porterr_count + 1
			#print("\n\n PortERR value is: " + str(porterr))
			#time.sleep(1)


	print('\n\nThe current status of all the switchports and the vlan information is provided below: ')

	print ("\nThe switchports in DOWN/Transciever Absent state are: " + str(portdown_count) + "\n")
	myfunc_log = myfunc_log + "\n\nThe switchports in DOWN/Transciever Absent state are: " + str(portdown_count) + "\n"
	myfunc_log = myfunc_log + str(portdown)
	print (portdown)
	print ("\nThe switchports  in UP state are: " + str(portup_count) + "\n")
	myfunc_log = myfunc_log + "\n\nThe switchports  in UP state are: " + str(portup_count) + "\n"
	myfunc_log = myfunc_log + str(portup)
	print (portup)
	print ("\nThe switchports  in ERR-DISABLE state are: " + str(porterr_count) + "\n")
	myfunc_log = myfunc_log + "\n\nThe switchports  in ERR-DISABLE state are: " + str(porterr_count) + "\n"
	myfunc_log = myfunc_log + str(porterr)
	print (porterr)

	
# The check for number of switchport change is put in try method so if user enters
# character or special characters the script will not proceed and the query wil be asked again
	
	done = False
	while not done:
		try:
			portnum_chg = int(input("How many switchports you want to change the vlan of: "))
			myfunc_log = myfunc_log + "\n\nThe number of switchport requested to change are: " + str(portnum_chg)
			done = True
		except ValueError:			
			print ("Please enter a numerical value.\nThe script won't proceed further and the input will be requested again.\n")	
			myfunc_log = myfunc_log + "\nPlease enter a numerical value.\nThe script won't proceed further and the input will be requested again.\n"
			#exit()

			
			
	portname_chg = ""
	switch_config = ""
	goodport = 0
		
	for z in range(0, portnum_chg):
		portvlannum_chg = ""
		voicevlannum_chg = ""
		description_chg = ""
		
		portname_chg = input("Enter the port name from the list provided above whose vlan is requested to be changed: ")
		myfunc_log = myfunc_log + "\n\nThe port name whose vlan is requested to change is: " + str(portname_chg)
		
# Try method used to ensure the data vlan number is a number and not alphabet or 
# any other special character.
		try:
			portvlannum_chg = int(input("Enter the data vlan number: "))
			myfunc_log = myfunc_log + "\nThe data vlan requested is: " + str(portvlannum_chg)
		except:
			print("\n\n The Data vlan was not provided in switchport configuration request or a non numerical value was provided. It wont be configured. ")
			myfunc_log = myfunc_log + "\nThe Data vlan was not provided in switchport configuration request or a non numerical value was provided. It wont be configured."
			#exit()

# Try method used to ensure the data vlan number is a number and not alphabet or 
# any other special character.
		try:
			voicevlannum_chg = int(input("Enter the Voice vlan number: "))
			myfunc_log = myfunc_log + "\nThe voice vlan requested is: " + str(portvlannum_chg)
		except:
			print("\n\n The Voice vlan was not provided in switchport configuration request or a non numerical value was provided. It wont be configured. ")
			myfunc_log = myfunc_log + "\nThe Voice vlan was not provided in switchport configuration request or a non numerical value was provided. It wont be configured."
			#exit()

# Accept description for the switchport from the user
		description_chg = input("Enter the description for the switchport: ")
		myfunc_log = myfunc_log + "\nThe description provided for the interface is: " + str(description_chg)	
			
# excp variables used to track exceptions in the checks for vlan number, interface mode and number
# in the code below 
		excp_trunk_routed_mtch = 0
		excp_int_name_mtch = 0
		excpvlanmtch = 0
		excpvoicevlanmtch = 0
		
		print("The requested port is: " + str(portname_chg))

# FOR loop to check if the number of interfaces to change are captured properly
		for i in range(0, numofinterfaces):

# IF statetment to check if the port number provided is present on the switch 
# If status of port is UP then it should not be a trunk or routed port
# If status of port is DOWN then it is ok if it is a trunk or routed port
			if str(portname_chg) == str(sh_int_status[i]['port']) and str(sh_int_status[i]['vlan']) != 'routed' and str(sh_int_status[i]['vlan']) != 'trunk':
				excp_int_name_mtch = excp_int_name_mtch + 1
				print ("Found the interface on the switch and the interface is an ACCESS port")
				myfunc_log = myfunc_log + "\n\nFound the interface on the switch and the interface is an ACCESS port"
				break
			elif str(portname_chg) == str(sh_int_status[i]['port']) and str(sh_int_status[i]['vlan']) == 'routed' and str(sh_int_status[i]['status']) != 'connected':
				excp_int_name_mtch = excp_int_name_mtch + 1
				print ("Found the interface on the switch and the interface is a ROUTED port with state DOWN")
				myfunc_log = myfunc_log + "\n\nFound the interface on the switch and the interface is a ROUTED port with state DOWN"
				break
			elif str(portname_chg) == str(sh_int_status[i]['port']) and str(sh_int_status[i]['vlan']) == 'trunk' and str(sh_int_status[i]['status']) != 'connected':
				excp_int_name_mtch = excp_int_name_mtch + 1
				print ("Found the interface on the switch and the interface is a TRUNK port with state DOWN")
				myfunc_log = myfunc_log + "\n\nFound the interface on the switch and the interface is a TRUNK port with state DOWN"
				break
			else:
				excp_int_name_mtch = 0

# For loop to run through all the vlans on the switch
		for q in range(0, numofvlan):
			x1 = int(sh_vlan[q]['vlan_id'])


# IF statetment to check if the data vlan requested matches the vlan on the switch			
			if portvlannum_chg == x1:		
				excpvlanmtch = excpvlanmtch + 1
				print ("The Data vlan is found on the switch")
				myfunc_log = myfunc_log + "\nThe Data vlan is found on the switch"
				break
#			elif portvlannum_chg == "":		
#				excpvlanmtch = 50
#				print ("The Data vlan was not provided in switchport configuration request. It wont be configured.")
#				break
			else:
				excpvlanmtch = 0

# For loop to run through all the vlans on the switch
		for q in range(0, numofvlan):
			x1 = int(sh_vlan[q]['vlan_id'])


# IF statetment to check if the voice vlan requested matches the vlan on the switch			
			if voicevlannum_chg == x1:		
				excpvoicevlanmtch = excpvoicevlanmtch + 1
				print ("The voice vlan is found on the switch")
				myfunc_log = myfunc_log + "\nThe Voice vlan is found on the switch"
				break
			elif voicevlannum_chg == "":		
				excpvoicevlanmtch = 50
				print ("The voice vlan was not provided in switchport configuration. It wont be configured.")
				myfunc_log = myfunc_log + "\nThe voice vlan was not provided in switchport configuration. It wont be configured."
				break
			else:
				excpvoicevlanmtch = 0
		
		
# IF statment to generate config for the requested port in case the exception
# flag in the exception variables are not set		
		if (excp_int_name_mtch != 0 and excpvlanmtch != 0 and (excpvoicevlanmtch == 1 or excpvoicevlanmtch == 50)):
			print (" The switchport configuration is: \n")
			myfunc_log = myfunc_log + "\n\nThe switchport configuration is: "
			
#			print ("default interface " + str(portname_chg))
#			switch_config = switch_config + "\ndefault interface " + str(portname_chg) + "\n"
			
			print ("interface " + str(portname_chg))
			switch_config = switch_config + "interface " + str(portname_chg) + "\n"
			
			print (" shutdown")
			switch_config = switch_config + " shutdown" + "\n"
			
			print (" description " + str(description_chg))
			switch_config = switch_config + " description " + str(description_chg) + "\n"
						
			print (" switchport \n switchport mode access \n switchport access vlan " + str(portvlannum_chg))
			switch_config = switch_config + " switchport \n switchport mode access \n switchport access vlan " + str(portvlannum_chg) + "\n"
			
			if excpvoicevlanmtch == 1:
				print (" switchport voice vlan " + str(voicevlannum_chg))
				switch_config = switch_config + " switchport voice vlan " + str(voicevlannum_chg) + "\n"				
			
			if ios_type == "IOS":
				print (" spanning-tree portfast")
				switch_config = switch_config + " spanning-tree portfast" + "\n"
			elif ios_type == "IOS-XE":
				print (" spanning-tree portfast edge")
				switch_config = switch_config + " spanning-tree portfast edge" + "\n"
			elif ios_type == "NXOS":
				print (" spanning-tree port type edge")
				switch_config = switch_config + " spanning-tree portfast" + "\n"
			
			print (" no shutdown \n")
			switch_config = switch_config + " no shutdown \n"
					
			goodport = goodport + 1	
			#time.sleep(5)
			
		elif excp_int_name_mtch == 0:
			print ("No matching interface found on switch or the switchport mode is not access or a trunk/routed port that is not down")
			myfunc_log = myfunc_log + "\nNo matching interface found on switch or the switchport mode is not access or a trunk/routed port that is not down"
		elif excpvlanmtch == 0:
			print ("The data vlan is not present on the switch")
			myfunc_log = myfunc_log + "\nThe data vlan is not present on the switch"
		elif excpvoicevlanmtch == 0:
			print ("The voice vlan is not present on the switch")	
			myfunc_log = myfunc_log + "\nThe voice vlan is not present on the switch"
		elif excpvoicevlanmtch == 50:
			print ("The voice vlan was not provided in switchport configuration. It wont be configured.")
			myfunc_log = myfunc_log + "\nThe voice vlan was not provided in switchport configuration. It wont be configured."


# Block to enter the do wr mem or copy run startup command depending on IOS, IOS-XE, NXOS
	if ios_type == "IOS":
		#print (" do wr mem")
		switch_config = switch_config + " do wr mem" + "\n"
		myfunc_log = myfunc_log + "\n" + str(switch_config)
	elif ios_type == "IOS-XE":
		#print (" do wr mem")
		switch_config = switch_config + " do wr mem" + "\n"
		myfunc_log = myfunc_log + "\n" + str(switch_config)
	elif ios_type == "NXOS":
		#print (" copy run start")
		switch_config = switch_config + " copy run start" + "\n"
		myfunc_log = myfunc_log + "\n" + str(switch_config)
			
# IF statement to track all the requested ports are good and to print the 
# final configuration			
	if goodport != 0:			
		print("\n\n")			
		print ("Total " + str(goodport) + " switchports will be configured.")
		myfunc_log = myfunc_log + "\n\nTotal " + str(goodport) + " switchports will be configured."
		print ("The Final configuration for the switchports is: \n" + str(switch_config))
		myfunc_log = myfunc_log + "The Final configuration for the switchports is: \n" + str(switch_config)
		#time.sleep(5)
		
		myfunc_log = myfunc_log + "\nPlease press ENTER if you want the script to configure the switchports: "
		input("\nPlease press ENTER if you want the script to configure the switchports: ")
		
		myfunc_log = myfunc_log + "\n\nAppending the logs of the myfunc function to the log file of the script."
		outfile_script_log = open(str(log_filename), "a")
		myfunc_log = myfunc_log + "\nWriting the logs of the function myfunc to the log file and then closing it."
		myfunc_log = myfunc_log + "\nSending the switchport configuration back to the main function."
		outfile_script_log.write(myfunc_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()
		
		return switch_config
	else:
		print("\n\nThe configuration could not be generated for the requested switchports.")
		myfunc_log = myfunc_log + "\n\nThe configuration could not be generated for the requested switchports."
		
		myfunc_log = myfunc_log + "\n\nAppending the logs of the myfunc function to the log file of the script."
		outfile_script_log = open(str(log_filename), "a")
		myfunc_log = myfunc_log + "\nWriting the logs of the function myfunc to the log file and then closing it."
		myfunc_log = myfunc_log + "\nSending the switchport configuration back to the main function."
		outfile_script_log.write(myfunc_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()





def myfunc1(final_switch_config, switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password):

	myfunc1_log = "" # Used to store the myfunc1 function logs

	myfunc1_log = myfunc1_log + "\n\n\n\n"
	myfunc1_log = myfunc1_log + "\n**************************************************************"
	myfunc1_log = myfunc1_log + "\n        The start of the myfunc1 funtion call"
	myfunc1_log = myfunc1_log + "\n**************************************************************"

	if ios_type == "IOS" or ios_type == "IOS-XE":
		#last_link_flapped = "last_input"
		print ("\nThe IOS type is: " + str(ios_type))
		myfunc1_log = myfunc1_log + "\nThe IOS type is: " + str(ios_type) 
		#time.sleep(3)
		
		if sshchk == 1:
	# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_ios',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '22',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for SSH")
			myfunc1_log = myfunc1_log + "\n\nThe connection handler is set for SSH with in the myfunc1 function since the switch responded to SSH socket check."
			#time.sleep(5)
		elif telnetchk == 1:
			# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_ios_telnet',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '23',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for TELNET")
			myfunc1_log = myfunc1_log + "\n\nThe connection handler is set for TELNET with in the myfunc1 function since the switch responded to TELNET socket check."
			#time.sleep(5)

		try:

# The defined connection handler connects to the IOS switch
			myfunc1_log = myfunc1_log + "\nTrying to connect to switch using Netmiko connection handler within the myfunc1 function."
			print("\nTrying to connect to switch using Netmiko connection handler within the myfunc1 function.")
			net_connect = ConnectHandler(**switch_cisco_ios)
			#net_connect.find_prompt()

# If the command execution fails then execute the exception block of commands			
			net_connect.enable()
			myfunc1_log = myfunc1_log + "\nSuccessfully connected to the switch.\nPLEASE WAIT !!! SWITCHPORT CONFIGURATION IN-PROGRESS."
			print ("Successfully connected to the switch.\nPLEASE WAIT !!! SWITCHPORT CONFIGURATION IN-PROGRESS.")
			
# Send the final_switch_config command block to the switch for configuration

			try:
				
				# Send the copy of all the commands in cmd list 
				# to the config_commands list
				exec_switch_eachrun = net_connect.send_config_set(final_switch_config, delay_factor=5, cmd_verify=False)
				print("The switchports are successfully configured and switch configuration is saved.")
				myfunc1_log = myfunc1_log + "\nThe switchports are successfully configured and switch configuration is saved."
				
# Close the ssh session of the device
				net_connect.disconnect()
				myfunc1_log = myfunc1_log + "\nDisconnected from the switch."
				print("Disconnected from the switch.")
				
			except:
				print ("\n The script connected to the switch but could not execute the commands due to some exception.")
				print ("Please check the commands supplied")
				myfunc1_log = myfunc1_log + "\n\nThe script connected to the switch but could not execute the commands due to some exception."
				myfunc1_log = myfunc1_log + "\nPlease check the commands supplied."
				pass
						
		except:
			print ("\n\nThe session could not be established with the switch.")
			print ("Please ensure the ip address or the switch name is correct and you are conecting to a switch and not a router.")
			print ("or the Switch name should have a correct DNS entry.")
			myfunc1_log = myfunc1_log + "\n\nThe session could not be established with the switch."
			myfunc1_log = myfunc1_log + "\nPlease ensure the ip address or the switch name is correct and you are conecting to a switch and not a router."
			myfunc1_log = myfunc1_log + "\nor the Switch name should have a correct DNS entry."

	elif ios_type == "NXOS":
		#last_link_flapped = "last_link_flapped"	
		print ("\n The IOS type is: " + str(ios_type))
		myfunc1_log = myfunc1_log + "\nThe IOS type is: " + str(ios_type)
		#time.sleep(3)		


		if sshchk == 1:
	# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_nxos',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '22',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for SSH")
			myfunc1_log = myfunc1_log + "\n\nThe connection handler is set for SSH with in the myfunc1 function since the switch responded to SSH socket check."
			#time.sleep(5)
		elif telnetchk == 1:
			# The connection handler parameters are defined to connect to the switch
			switch_cisco_ios = {
						'device_type': 'cisco_nxos_telnet',
						'ip': str(switch_name_ip),
						'username': str(username),
						'password': str(password),
						'secret': str(password),
						'port': '23',
						'verbose': 'True',
			#			"global_delay_factor": 4
						}
			print("The connection handler within the Function is set for TELNET")
			myfunc1_log = myfunc1_log + "\n\nThe connection handler is set for TELNET with in the myfunc1 function since the switch responded to TELNET socket check."
			#time.sleep(5)
			
		try:

# The defined connection handler connects to the IOS switch
			myfunc1_log = myfunc1_log + "\nTrying to connect to switch using Netmiko connection handler within the myfunc1 function."
			print("\nTrying to connect to switch using Netmiko connection handler within the myfunc1 function.")
			net_connect = ConnectHandler(**switch_cisco_ios)
			#net_connect.find_prompt()

# If the command execution fails then execute the exception block of commands			
			net_connect.enable()
			myfunc1_log = myfunc1_log + "\nSuccessfully connected to the switch.\nPLEASE WAIT !!! SWITCHPORT CONFIGURATION IN-PROGRESS."
			print ("Successfully connected to the switch.\nPLEASE WAIT !!! SWITCHPORT CONFIGURATION IN-PROGRESS.")
			
# Send the final_switch_config command block to the switch for configuration
			try:
						
				# Send the copy of all the commands in cmd list 
				# to the config_commands list
				exec_switch_eachrun = net_connect.send_config_set(final_switch_config, delay_factor=5, cmd_verify=False)
				print("The switchports are successfully configured and switch configuration is saved.")
				myfunc1_log = myfunc1_log + "\nThe switchports are successfully configured and switch configuration is saved."
				
# Close the ssh session of the device
				net_connect.disconnect()					
				myfunc1_log = myfunc1_log + "\nDisconnected from the switch."
				print("Disconnected from the switch.")
				
			except:
				print ("\n The script connected to the switch but could not execute the commands due to some exception.")
				print ("Please check the commands supplied")
				myfunc1_log = myfunc1_log + "\n\nThe script connected to the switch but could not execute the commands due to some exception."
				myfunc1_log = myfunc1_log + "\nPlease check the commands supplied."
				pass		
		
		except:
			print ("The session could not be established with the switch.")
			print ("Please ensure the ip address or the switch name is correct and you are conecting to a switch and not a router.")
			print ("Switch name should have a correct DNS entry.")
			myfunc1_log = myfunc1_log + "\n\nThe session could not be established with the switch."
			myfunc1_log = myfunc1_log + "\nPlease ensure the ip address or the switch name is correct and you are conecting to a switch and not a router."
			myfunc1_log = myfunc1_log + "\nor the Switch name should have a correct DNS entry."
			
	myfunc1_log = myfunc1_log + "\n\nAppending the logs of the myfunc1 function to the log file of the script."
	outfile_script_log = open(str(log_filename), "a")
	myfunc1_log = myfunc1_log + "\nWriting the logs of the function myfunc1 to the log file and then closing it."
	outfile_script_log.write(myfunc1_log)
#	# Close the log file opened for saving the logs
	outfile_script_log.close()	
	
#	print (myfunc1_log)
	return




def FUNC_EMAIL_SEND(final_switch_config, switch_name_ip, username):


	# **********************************************************************
	# Block to send email of all script successful run  
	# to the email recipients 
	# **********************************************************************

		
	# SMTP server cariable definition
	smtp_port = 25
	#smtp_server = "ENTERE_SMTP_SEVER_IP_OR_FQDN"
	#smtp_login = "ENTER_SMTP_USERNAME"
	#smtp_password = "ENTER_SMTP_PASSWORD"
	smtp_server = "ENTERE_SMTP_SEVER_IP_OR_FQDN"


	# specify the sender’s and receiver’s email addresses
	sender = "ENTER_SENDER_EMAIL_ID"
	#receiver = "ENTER_RECEIVER_EMAIL_ID"
	receiver = "ENTER_RECEIVER_EMAIL_ID"


	# type your message: use two newlines (\n) to separate the subject from the message body, and use 'f' to  automatically insert variables in the text

	message = """\
	Subject: Switchport configuration status email
	To: """+str(receiver)+"""
	From: """+str(sender)+"""

	The script ran successfully for the switchport configuration of the switch """+str(switch_name_ip)+""".
	The script was initiated by the user: """+str(username)+"""


	******************************************************
	The configuration of the switchport is mentioned below: 
	"""+str(final_switch_config)+"""
	******************************************************



	Regards,
	Friendly Neighborhood,
	Net-L2-Atom !!! :)


	"""	
		
	try:
		# send your message with credentials specified above
		with smtplib.SMTP(smtp_server, smtp_port) as server:
			server.login(smtp_login, smtp_password)
			server.sendmail(sender, receiver, message.encode('utf8'))
		#print(message)
		# tell the script to report if your message was sent or which errors need to be fixed 
			print("The script ran successfully and email was send.")
			#script_log = script_log + "\nThe script ran successfully and email was send."

	except (gaierror, ConnectionRefusedError):
		print("Failed to connect to the EMAIL server. Bad connection settings?")
		#script_log = script_log + "\nFailed to connect to the EMAIL server. Bad connection settings?"

	except smtplib.SMTPServerDisconnected:
		print("Failed to connect to the EMAIL server. Wrong user/password?")
		#script_log = script_log + "\nFailed to connect to the EMAIL server. Bad connection settings?"

	except smtplib.SMTPException as e:
		print("SMTP error occurred: " + str(e))	
		#script_log = script_log + "\nSMTP error occurred: " + str(e)	
		



	return


switch_name_ip = input("Enter the name or ip address of the switch: ")

script_log = "\nThe name/ip address of the switch provided is: " + str(switch_name_ip) + "\n"

	
username = input('Enter your Username: ')
password = getpass.getpass('Enter your Password: ') 	

script_log = script_log + "\nEnter your Username: "
script_log = script_log + username
script_log = script_log + "\nEnter your Password: "
#script_log = script_log + password



# Create a name of the log file for every switch name/ip provided
log_filename = str(switch_name_ip) + "_log" + str(log_file_datestr) + ".txt"


# The block of code below is to check if the switch responds to TELNET or SSH.

# Create a socket object by calling socket.socket(family, type) with family set to socket.AF_INET and type set to socket.SOCK_STREAM. 
# socket.AF_INET specifies the IP address family for IPv4 and socket.SOCK_STREAM specifies the socket type for TCP.	
a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
script_log = script_log + "\nA socket object is defined for SSH."

# Check if the switch responds to SSH.
switchconnect = (switch_name_ip, 22)
result_of_sshcheck = a_socket.connect_ex(switchconnect)

script_log = script_log + "\nThe socket object is checking if the switch reposnds to SSH."

if result_of_sshcheck == 0:
   print("The switch responds to SSH.")
   script_log = script_log + "\nThe socket object has confirmed the switch responds to SSH."
   sshchk = 1
   #print("The value set for variable check: " + str(sshchk))
   #time.sleep(5)
else:
   print("The switch does not responds to SSH.")
   script_log = script_log + "\nThe socket object has confirmed the switch does not responds to SSH."
   sshchk = 0
   #print("The value set for variable check: " + str(sshchk))
   #time.sleep(5)

a_socket.close()
script_log = script_log + "\nThe socket object has closed the SSH socket to the switch."


# Create a socket object by calling socket.socket(family, type) with family set to socket.AF_INET and type set to socket.SOCK_STREAM. 
# socket.AF_INET specifies the IP address family for IPv4 and socket.SOCK_STREAM specifies the socket type for TCP.	
a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
script_log = script_log + "\n\nA socket object is defined for TELNET."


# Check if the switch responds to TELNET.
switchconnect = (switch_name_ip, 23)
result_of_telnetcheck = a_socket.connect_ex(switchconnect)
script_log = script_log + "\nThe socket object is checking if the switch reposnds to TELNET."

if result_of_telnetcheck == 0:
	print("The switch responds to TELNET.")
	script_log = script_log + "\nThe socket object has confirmed the switch responds to TELNET."
	telnetchk = 1
    #print("The value set for variable check: " + str(telnetchk))
    #time.sleep(5)
else:
   print("The switch does not responds to TELNET.")
   script_log = script_log + "\nThe socket object has confirmed the switch does not responds to TELNET."
   telnetchk = 0
   #print("The value set for variable check: " + str(telnetchk))
   #time.sleep(5)

a_socket.close()
script_log = script_log + "\nThe socket object has closed the TELNET socket to the switch."



if sshchk == 1:
	# The connection handler parameters are defined to connect to the switch
	switch_cisco_ios = {
				'device_type': 'cisco_ios',
				'ip': str(switch_name_ip),
				'username': str(username),
				'password': str(password),
				'secret': str(password),
				'port': '22',
				'verbose': 'True',
				"global_delay_factor": 4
				}
	print("The connection handler is set for SSH since the switch responded to SSH socket check.")
	script_log = script_log + "\n\nThe connection handler is set for SSH since the switch responded to SSH socket check."
	#time.sleep(5)
	
elif telnetchk == 1:
	# The connection handler parameters are defined to connect to the switch
	switch_cisco_ios = {
				'device_type': 'cisco_ios_telnet',
				'ip': str(switch_name_ip),
				'username': str(username),
				'password': str(password),
				'secret': str(password),
				'port': '23',
				'verbose': 'True',
				"global_delay_factor": 4
				}
	print("The connection handler is set for TELNET since the switch responded to TELNET socket check.")
	script_log = script_log + "\n\nThe connection handler is set for TELNET since the switch responded to TELNET socket check."
	#time.sleep(5)

else:
	print("\n\nThe switch does not respond to SSH or TELNET. \nPlease check with the network team if the switch is configured properly or there is a firewall blocking the access.")
	script_log = script_log + "\n\nThe switch does not respond to SSH or TELNET. \nPlease check with the network team if the switch is configured properly or there is a firewall blocking the access."
		
	
	script_log = script_log + "\n\nCreating a file to save the logs of the script."
	outfile_script_log = open(str(log_filename), "a")
	script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
	outfile_script_log.write(script_log)
	# Close the log file opened for saving the logs
	outfile_script_log.close()
	
	input("\nPlease press ENTER to leave: ")
	exit()	
		
		
try:

# The defined connection handler is called in the netmiko to connect to the switch 
# If the connect handler fails then execute the exception block of commands	
	script_log = script_log + "\nTrying to connect to switch using Netmiko connection handler to capture the show version command."
	print("\nTrying to connect to switch using Netmiko connection handler to capture the show version command.")
	net_connect = ConnectHandler(**switch_cisco_ios)
	#net_connect.find_prompt()
	script_log = script_log + "\nSuccessfully connected to the switch."
	
# If the command execution fails then execute the exception block of commands			
	net_connect.enable()

# Get the output of the show ver command
	sh_ver = net_connect.send_command('show version', cmd_verify=False)
	script_log = script_log + "\nSuccessfully captured the show version command."
	
# Close the ssh session of the device
	net_connect.disconnect()
	script_log = script_log + "\nDisconnected from the switch."
	
except:
	print ("The session could not be established with the switch.")
	print ("Please ensure the ip address or the switch name is correct and you are conecting to a switch and not a router.")
	print ("or the Switch name should have a correct DNS entry.")
	script_log = script_log + "\n\nThe session could not be established with the switch."
	script_log = script_log + "\nPlease ensure the ip address or the switch name is correct and you are conecting to a switch and not a router."
	script_log = script_log + "\nor the Switch name should have a correct DNS entry."
	
	
	script_log = script_log + "\n\nCreating a file to save the logs of the script."
	outfile_script_log = open(str(log_filename), "a")
	script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
	outfile_script_log.write(script_log)
	# Close the log file opened for saving the logs
	outfile_script_log.close()
	
	input("\nPlease press ENTER to leave: ")
	

else:						

	final_switch_config = " "

	script_log = script_log + "\n\nTrying to determine is switch is running IOS, IOS-XE, NXOS code"
	script_log = script_log + "\nbased on the show version command captured earlier"
	
# Check if the switch is Cisco IOS, Cisco NX-OS, Cisco IOS-XE
	if sh_ver.find("Cisco IOS Software, IOS-XE Software,") == 0  or sh_ver.find("IOS-XE") != -1 or sh_ver.find("XE") != -1 or "IOS-XE" in sh_ver or "IOS XE" in sh_ver:
		print("\nThe switch is identified to be running Cisco IOS-XE software.")
		script_log = script_log + "\n\nThe switch is identified to be running Cisco IOS-XE software."
		ios_type = "IOS-XE"

		script_log = script_log + "\nPlacing a call for the 1st function from the main script to generate the switchport config."
		
		script_log = script_log + "\n\nCreating a file to save the logs of the script."
		outfile_script_log = open(str(log_filename), "w")
		script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
		outfile_script_log.write(script_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()
		
		final_switch_config = myfunc(switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password)

		script_log = ""
		script_log = script_log + "\n\nPlacing a call for the 2nd function from the main script to configure the switchport."
		
		script_log = script_log + "\n\nCreating a file to save the logs of the script."
		outfile_script_log = open(str(log_filename), "a")
		script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
		outfile_script_log.write(script_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()

		if final_switch_config:
			myfunc1(final_switch_config, switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password)

		
		FUNC_EMAIL_SEND(final_switch_config, switch_name_ip, username)
		
		
		input("\nPlease press ENTER to leave: ")
		
	elif sh_ver.find("Cisco IOS Software, ") == 0 or sh_ver.find("Cisco IOS Software, ") != -1 or sh_ver.find("Cisco Internetwork Operating System Software") != -1 or "Cisco IOS Software, " in sh_ver or "Cisco Internetwork Operating System Software" in sh_ver or "IPBASE" in sh_ver or "UNIVERSALK9" in sh_ver or "LANBASEK9" in sh_ver:
		print("\nThe switch is identified to be running Cisco IOS software. ")
		script_log = script_log + "\n\nThe switch is identified to be running Cisco IOS software."
		ios_type = "IOS"

		script_log = script_log + "\nPlacing a call for the 1st function from the main script to generate the switchport config."
		
		script_log = script_log + "\n\nCreating a file to save the logs of the script."
		outfile_script_log = open(str(log_filename), "w")
		script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
		outfile_script_log.write(script_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()

		final_switch_config = myfunc(switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password)

		script_log = ""
		script_log = script_log + "\n\nPlacing a call for the 2nd function from the main script to configure the switchport."
		
		script_log = script_log + "\n\nCreating a file to save the logs of the script."
		outfile_script_log = open(str(log_filename), "a")
		script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
		outfile_script_log.write(script_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()

		if final_switch_config:
			myfunc1(final_switch_config, switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password)

		
		FUNC_EMAIL_SEND(final_switch_config, switch_name_ip, username)

		
		input("\nPlease press ENTER to leave: ")
		
	elif sh_ver.find("Cisco Nexus Operating System (NX-OS) Software") == 0 or  sh_ver.find("Cisco Nexus Operating System (NX-OS) Software") != -1 or sh_ver.find("NX-OS") != -1 or "Cisco Nexus Operating System (NX-OS) Software" in sh_ver or "NX-OS" in sh_ver or "Cisco Nexus Operating System" in sh_ver or "NXOS" in sh_ver:
		print("\nThe switch is identified to be running Cisco NXOS software. ")
		script_log = script_log + "\n\nThe switch is identified to be running Cisco NXOS software."
		ios_type = "NXOS"

		script_log = script_log + "\nPlacing a call for the 1st function from the main script to generate the switchport config."
		
		script_log = script_log + "\n\nCreating a file to save the logs of the script."
		outfile_script_log = open(str(log_filename), "w")
		script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
		outfile_script_log.write(script_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()

		final_switch_config = myfunc(switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password)

		script_log = ""
		script_log = script_log + "\n\nPlacing a call for the 2nd function from the main script to configure the switchport."
		
		script_log = script_log + "\n\nCreating a file to save the logs of the script."
		outfile_script_log = open(str(log_filename), "a")
		script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
		outfile_script_log.write(script_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()

		if final_switch_config:
			myfunc1(final_switch_config, switch_name_ip, ios_type, sshchk, telnetchk, log_filename, username, password)
		
		FUNC_EMAIL_SEND(final_switch_config, switch_name_ip, username)
		
		input("\nPlease press ENTER to leave: ")
		
	else:
		print ("\nThe device name/ipaddress you provided is not a Cisco IOS, IOS-XE or NxOS switch.\nThe vlan changes will not be performed.")
		script_log = script_log + "\nThe device name/ipaddress you provided is not a Cisco IOS, IOS-XE or NxOS switch.\nThe vlan changes will not be performed."
		
		script_log = script_log + "\n\nCreating a file to save the logs of the script."
		outfile_script_log = open(str(log_filename), "a")
		script_log = script_log + "\nWriting the logs of the script to the log file and then closing it."
		outfile_script_log.write(script_log)
		# Close the log file opened for saving the logs
		outfile_script_log.close()
		
		input("\nPlease press ENTER to leave: ")