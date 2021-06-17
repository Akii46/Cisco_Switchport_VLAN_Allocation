# Cisco_Switchport_VLAN_Allocation
The script performs switchport vlan change on Cisco IOS, IOS-XE and NXOS devices only. Vlan of switch ports with mode access are changed, Trunk and routed interface vlan assignments are changed if those ports are DOWN and not if they are UP

# Script Pre-requisites to run:
# 1. Install netmiko and paramiko module 
# 2. Install netaddr module
# 3. Install ipaddr module
# 4. Define the NET_TEXTFSM= path
#    For Windows/Linux/MacOS: https://www.schrodinger.com/kb/1842
#    For Linux: https://pynet.twb-tech.com/blog/automation/netmiko-textfsm.html
#    you should also edit the ntc template cisco_ios_show_interfaces_status.textfsm to include the NXOS notconnec & xcvrAbsen interface status to match, you can just copy paste the ntc template i've provided with the repo.
