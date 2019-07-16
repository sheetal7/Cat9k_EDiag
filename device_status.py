#!/usr/bin/env python2
from __future__ import print_function

"""Sample Device Status Monitoring Application

Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

#__author__ = "Sheetal Sahasrabudge <sheesaha@cisco.com>"\
#__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
#__license__ = "Cisco Sample Code License, Version 1.1"


from ncclient import manager
import xmltodict
import json
from json2html import *
import cgi;
import cgitb;

# Catalyst 9K switch hostname or IP address
HOSTNAME = "172.24.102.141"

# Catalyst 9K switch Netconf port
PORT = 830 

# Catalyst 9K switch login credentials
USERNAME = "cisco"
PASSWORD = "cisco123"

# Interface of which status is monitored
#INTERFACE_NAME = "GigabitEthernet0/0"
INTERFACE_NAME = "AppGigabitEthernet1/0/1"

kr_results = []

def get_state_data(host, port, user, pwd, ep, intf):
    """Fetch state of the interface from the switch.

    Open a Netconf connection to the switch and fetch
    state of the specified interface.

    Args:
        host (str): Switch hostname or IP address.
        port (str): Switch Netconf port number.
        user (str): Switch login username.
        pwd (str) : Switch login password.
        intf (str): Interface of which state to fetch.

    Returns:
        str: The XML encoded response from the switch.
    
    filter_string = "/interfaces/interface[name='" + intf + "']/state"
    with manager.connect(host=host, port=port, \
                         username=user, password=pwd, \
                         allow_agent=False, look_for_keys=False, \
                         hostkey_verify=False) as m:
        intf_state_xml = m.get(filter=("xpath", filter_string)).data_xml
    """
    intf_state_xml = ""
    #filter_string = "/interfaces/interface[name='" + intf + "']/oper_status"
    filter_string = "/"
    #filter_string = "/{}s/{}[name='{}']".format(ep, ep, intf)
    print(filter_string)
    with manager.connect(host=host, port=port, \
                         username=user, password=pwd, \
                         allow_agent=False, look_for_keys=False, \
                         hostkey_verify=False) as m:
        sys_state_xml = m.get(filter=("xpath", filter_string)).data_xml
    print("filter string: " + filter_string)
    print("******************************************")
    print(json.dumps(sys_state_xml, indent=2))
    print("******************************************")
    return intf_state_xml



def get_intf_state_data(host, port, user, pwd, intf):
    """Fetch state of the interface from the switch.

    Open a Netconf connection to the switch and fetch
    state of the specified interface.

    Args:
        host (str): Switch hostname or IP address.
        port (str): Switch Netconf port number.
        user (str): Switch login username.
        pwd (str) : Switch login password.
        intf (str): Interface of which state to fetch.

    Returns:
        str: The XML encoded response from the switch.
    
    filter_string = "/interfaces/interface[name='" + intf + "']/state"
    with manager.connect(host=host, port=port, \
                         username=user, password=pwd, \
                         allow_agent=False, look_for_keys=False, \
                         hostkey_verify=False) as m:
        intf_state_xml = m.get(filter=("xpath", filter_string)).data_xml
    """
    intf_state_xml = ""
    #filter_string = "/interfaces/interface[name='" + intf + "']/oper_status"
    filter_string = "/interfaces/interface[name='" + intf + "']"
    with manager.connect(host=host, port=port, \
                         username=user, password=pwd, \
                         allow_agent=False, look_for_keys=False, \
                         hostkey_verify=False) as m:
        intf_state_xml = m.get(filter=("xpath", filter_string)).data_xml
        print("filter string: " + filter_string)
    return intf_state_xml


def extract_intf_state(intf_state_xml):
    """Save interface state as Python dictionary.

    Convert interface state from XML encoded string to
    a Python dictionary object.

    Args:
        intf_state_xml (str): XML encoded interface state.

    Returns:
        dict: Interface state.
    
    """

    intf_state = xmltodict.parse(intf_state_xml)

    return intf_state



descs = {
   "in-errors": "k",
   "in-mac-control-frames": "0",
   "in-mac-pause-frames": "0",
   "in-octets": "164902",
   "out-errors": "0",
   "out-mac-control-frames": "0",
   "out-mac-pause-frames": "0",
   "out-octets": "132751042"
}

def output_extra(intf_state):
    intr = intf_state['data']['interfaces']['interface']
    intr['ether-state']

    stats = {}
    stats_table = {
        'statistics': ['in-octets', 'out-octets', 'in-errors', 'out-errors'],
        'ether-stats': ['in-mac-control-frames', 'in-mac-pause-frames', 'out-mac-control-frames', 'out-mac-pause-frames']}

    for key, subkeys in stats_table.items():
        for subkey in subkeys:
            stats[subkey] = intr[key][subkey]

    ds = []
    for k, v in stats.items():
        ds.append({
            "key": k,
            "Title": titles[k],
            "Desc": descs[k],
            "value": v,
            "status": get_status(v)
            })


    return intr['ether-state'], stats, ds
        

def summary_table(intf_state):
    summary = []
    intr = intf_state['data']['interfaces']['interface']
    if intr['admin-status'] == "if-state-up":
        summary.append({"name": "Application hosting interface is up", "status": "1"})
    else:
        summary.append({"name": "Application hosting interface is down", "status": "0"})

    print("IN-ERRORS type=", type(intr['statistics']['in-errors']))
    if ( (int(intr['statistics']['in-errors']) != 0) or (int(intr['statistics']['out-errors']) != 0)):
        summary.append("Packet errors were seen on the interface, check interface statistics for details")
    else:
        summary.append("No packet errors seen on the interface")
    if ( (int(intr['ether-stats']['in-mac-pause-frames']) != 0) or (int(intr['ether-stats']['out-mac-pause-frames']) != 0)):
        summary.append("MAC pause were seen on the interface, check interface statistics for details")
    else:
        summary.append("No MAC Pause frames seen on the interface")
    return summary
        
def output_summary(intf_state):
    result = {}
    print(json.dumps(intf_state, indent=2))
    intr = intf_state['data']['interfaces']['interface']
    
    print(intr['name'], intr['admin-status'], intr['oper-status'])
    result['Test'] = "Interface status"
    if intr['admin-status'] == "if-state-up":
        result['Status'] = "PASS"
        result['Result'] = "App-hosting interface is up"
    else :
        print(intr['admin-status'])
        result['Status'] = "FAIL"
        result['Result'] = "App-hosting interface is down"
    result['Test Group'] = "KR Port"
    #kr_results.append(result)

    result1 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['statistics']
    result1['Test'] = "Interface output packet error counts"
    if (intr_stats['out-errors'] != "0") :
        result1['Status'] = "FAIL"
        result1['Result'] = "Output Packet errors seen on App interface, error count=" + intr_stats['out-errors']
    else :
        result1['Status'] = "PASS"
        result1['Result'] = "No output Packet errors seen on App interface"
    result1['Test Group'] = "KR Port"
    #kr_results.append(result1)

    result2 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['statistics']
    result2['Test'] = "Interface input packet error counts"
    if (intr_stats['in-errors'] != "0") :
        result2['Status'] = "FAIL"
        result2['Result'] = "Input Packet errors seen on App interface, error count=" + intr_stats['in-errors'] 
    else :
        result2['Status'] = "PASS"
        result2['Result'] = "No input Packet errors seen on App interface"
    result2['Test Group'] = "KR Port"
    #kr_results.append(result2)

    result3 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['ether-stats']
    result3['Test'] = "App interface output Pause Frames"
    if (intr_stats['out-mac-pause-frames'] != "0") :
        result3['Status'] = "FAIL"
        result3['Result'] = "Output Pause frames have been sent on App interface, error count=" + intr_stats['out-mac-pause-frames']
    else :
        result3['Status'] = "PASS"
        result3['Result'] = "No output Pause frames have been sent on App interface"
    result3['Test Group'] = "KR Port"
    #kr_results.append(result3)

    result4 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['ether-stats']
    result4['Test'] = "Interface input Pause Frames"
    if (intr_stats['in-mac-pause-frames'] != "0") :
        result4['Status'] = "FAIL"
        result4['Result'] = "Input Pause frames have been sent on App interface, error count=" + intr_stats['in-mac-pause-frames']
    else :
        result4['Status'] = "PASS"
        result4['Result'] = "No input Pause frames have been sent on App interface"
    result4['Test Group'] = "KR Port"
    #kr_results.append(result4)


def filter_results(res, remove):
    for rs in res:
        for rk in remove:
            del rs[rk]

    
def output_intf_state(intf, intf_state):
    """Output interface state as HTML webpage.

    Generate an HTML webpage displaying interface state
    and providing a Refresh link.

    Args:
        intf (str)       : Interface name.
        intf_state (dict): Interface state dictionary.

    """

    f = open('edge_analytics.html','w')
    cgitb.enable()

    print("Content-Type: text/html")
    print("")

    print("<h1>Cat9K switch Overall health</h1>")
    print("<h2>App-hosting Interface " + intf + " Status</h2>")
    print("<a href=\"javascript:window.location.reload(true)\">Refresh</a>")
    print(json2html.convert(json.dumps(intf_state)))

    f.write("<a href=\"javascript:window.location.reload(true)\">Refresh</a>")
    f.write("<h1>Overall switch health</h1>")
    f.write("<h2>App-hosting Interface " + intf + " Status</h2>")

    summary = summary_table(intf_state)
    f.write(json2html.convert(json.dumps(summary)))
    
    filter_results(kr_results, ["Status", "Test Group"])
    f.write(json2html.convert(json.dumps(kr_results)))

    state, stats, _ = output_extra(intf_state)
    f.write("<h2> State </h2>")
    f.write(json2html.convert(json.dumps(state)))
    f.write("<h2> Stats </h2>")
    f.write(json2html.convert(json.dumps(stats)))

    f.close()
    return


def summary_html(intf_state):
    s = summary(intf_state)

    out = ""
    out += "<h2> Summary </h2>\n"
    out += json2html.convert(json.dumps(s["summary"]))
    out += "\n<h2> State </h2>\n"
    out += json2html.convert(json.dumps(s["state"]))
    out += "\n<h2> Stats </h2>\n"
    out += json2html.convert(json.dumps(s["stats"]))
    return out

def summary(intf_state):
    state, stats, ds = output_extra(intf_state)
   
    optable = summary_table(intf_state)
    
    return {
        "summary": optable,
        "state": ds,
        "stats": stats}
   

def get_intf_state():
    intf_state_xml = get_intf_state_data(HOSTNAME, PORT, \
                                         USERNAME, PASSWORD, \
                                         INTERFACE_NAME)
    intf_state = extract_intf_state(intf_state_xml)
    return intf_state
    

if __name__ == '__main__':
    intf_state = get_intf_state()
    output_summary(intf_state)
    print(json.dumps(kr_results, indent=2))
    output_intf_state(INTERFACE_NAME, intf_state)


