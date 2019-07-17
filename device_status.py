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

#__author__ = "Sheetal Sahasrabudge <sheesaha@cisco.com>, Shikhar Suryavansh <shisurya@cisco.com>"\
#__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
#__license__ = "Cisco Sample Code License, Version 1.1"


from ncclient import manager
import xmltodict
import json
from json2html import *
import cgi
import cgitb
import sys
import telnetlib
import time
import json
import re

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
    # print(filter_string)
    with manager.connect(host=host, port=port,
                         username=user, password=pwd,
                         allow_agent=False, look_for_keys=False,
                         hostkey_verify=False) as m:
        sys_state_xml = m.get(filter=("xpath", filter_string)).data_xml
    # print("filter string: " + filter_string)
    # print("******************************************")
    # print(json.dumps(sys_state_xml, indent=2))
    # print("******************************************")
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
    with manager.connect(host=host, port=port,
                         username=user, password=pwd,
                         allow_agent=False, look_for_keys=False,
                         hostkey_verify=False) as m:
        intf_state_xml = m.get(filter=("xpath", filter_string)).data_xml
        # print("filter string: " + filter_string)
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
    "auto-negotiate": "Link will suto-negotiate parameters",
    "enable-flow-control": "Flow control enable/disable staus",
    "negotiated-duplex-mode": "Duplex mode for the link",
    "negotiated-port-speed": "Link speed"
}

titles = {
    "auto-negotiate": "Auto negotiation",
    "enable-flow-control": "Flow control",
    "negotiated-duplex-mode": "Duplex mode",
    "negotiated-port-speed": "Link speed"
}

stats_descs = {
    "in-octets": "Input octets count",
    "out-octets": "Output octets count",
    "in-errors": "Input errors count",
    "out-errors": "Output errors count",
    "in-mac-control-frames": "Input MAC control frames count",
    "out-mac-control-frames": "Output MAC control frames count",
    "in-mac-pause-frames": "Input MAC pause frames count",
    "out-mac-pause-frames": "Output MAC pause frames count"
}

stats_titles = {
    "in-octets": "Input octets",
    "out-octets": "Output octets",
    "in-errors": "Input errors",
    "out-errors": "Output errors",
    "in-mac-control-frames": "Input MAC control frames",
    "out-mac-control-frames": "Output MAC control frames",
    "in-mac-pause-frames": "Input MAC pause frames",
    "out-mac-pause-frames": "Output MAC pause frames"
}

iox_descs = {
    "IOx service (IOxman)     ": "IOxman service",
    "Libvirtd   1.3.4         ": "Libvirtd service",
    "IOx service (HA)         ": "HA service",
    "IOx service (CAF) 1.8.0.2": "CAF service",
    "Dockerd    18.03.0       ": "Dockerd service"
}

iox_titles = {
    "IOx service (IOxman)     ": "IOxman",
    "Libvirtd   1.3.4         ": "Libvirtd",
    "IOx service (HA)         ": "HA",
    "IOx service (CAF) 1.8.0.2": "CAF",
    "Dockerd    18.03.0       ": "Dockerd"
}

appList_descs = {
    "monitor_iox": "monitor app",
}

appList_titles = {
    "monitor_iox": "monitor",
}

res_descs = {
    "StorageAvail": "Available storage resource",
    "MemoryQuota": "Total memory resource",
    "CPUQuota": "Total CPU resource",
    "StorageQuota": "Total storage resource",
    "MemoryAvail": "Available memory resource",
    "CPUAvail": "Available CPU resource"
}

res_titles = {
    "StorageAvail": "Available storage",
    "MemoryQuota": "Total memory",
    "CPUQuota": "Total CPU",
    "StorageQuota": "Total storage",
    "MemoryAvail": "Available memory",
    "CPUAvail": "Available CPU"
}


def get_status(val):
    return "true"


def output_extra(intf_state):
    intr = intf_state['data']['interfaces']['interface']
    lstate = intr['ether-state']

    stats = {}
    stats_table = {
        'statistics': ['in-octets', 'out-octets', 'in-errors', 'out-errors'],
        'ether-stats': ['in-mac-control-frames', 'in-mac-pause-frames', 'out-mac-control-frames', 'out-mac-pause-frames']}

    for key, subkeys in stats_table.items():
        for subkey in subkeys:
            stats[subkey] = intr[key][subkey]

    ds = []
    for k, v in lstate.items():
        ds.append({
            "key": k,
            "title": titles[k],
            "desc": descs[k],
            "value": v,
            "status": get_status(v)
        })

    stats_ds = []
    for k, v in stats.items():
        stats_ds.append({
            "key": k,
            "title": stats_titles[k],
            "desc": stats_descs[k],
            "value": v,
            "status": get_status(v)
        })

    return intr['ether-state'], stats, ds, stats_ds


def summary_table(intf_state, ioxInfo):
    summary = []
    intr = intf_state['data']['interfaces']['interface']
    if intr['admin-status'] == "if-state-up":
        summary.append(
            {"name": "Application hosting interface is up", "status": "1"})
    else:
        summary.append(
            {"name": "Application hosting interface is down", "status": "0"})

    # print("IN-ERRORS type=", type(intr['statistics']['in-errors']))
    if ((int(intr['statistics']['in-errors']) != 0) or (int(intr['statistics']['out-errors']) != 0)):
        summary.append(
            {"name": "Packet errors were seen on the interface, check interface statistics for details", "status": "0"})
    else:
        summary.append(
            {"name": "No packet errors seen on the interface", "status": "1"})
    if ((int(intr['ether-stats']['in-mac-pause-frames']) != 0) or (int(intr['ether-stats']['out-mac-pause-frames']) != 0)):
        summary.append(
            {"name": "MAC pause were seen on the interface, check interface statistics for details", "status": "0"})
    else:
        summary.append(
            {"name": "No MAC Pause frames seen on the interface", "status": "1"})
    if(checkRunning(ioxInfo)):
        summary.append({"name": "All iox services are running", "status": "1"})
    else:
        summary.append(
            {"name": "All iox services are not running, check iox for details", "status": "0"})

    return summary


def output_summary(intf_state):
    result = {}
    # print(json.dumps(intf_state, indent=2))
    intr = intf_state['data']['interfaces']['interface']

    # print(intr['name'], intr['admin-status'], intr['oper-status'])
    result['Test'] = "Interface status"
    if intr['admin-status'] == "if-state-up":
        result['Status'] = "PASS"
        result['Result'] = "App-hosting interface is up"
    else:
        # print(intr['admin-status'])
        result['Status'] = "FAIL"
        result['Result'] = "App-hosting interface is down"
    result['Test Group'] = "KR Port"
    # kr_results.append(result)

    result1 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['statistics']
    result1['Test'] = "Interface output packet error counts"
    if (intr_stats['out-errors'] != "0"):
        result1['Status'] = "FAIL"
        result1['Result'] = "Output Packet errors seen on App interface, error count=" + \
            intr_stats['out-errors']
    else:
        result1['Status'] = "PASS"
        result1['Result'] = "No output Packet errors seen on App interface"
    result1['Test Group'] = "KR Port"
    # kr_results.append(result1)

    result2 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['statistics']
    result2['Test'] = "Interface input packet error counts"
    if (intr_stats['in-errors'] != "0"):
        result2['Status'] = "FAIL"
        result2['Result'] = "Input Packet errors seen on App interface, error count=" + \
            intr_stats['in-errors']
    else:
        result2['Status'] = "PASS"
        result2['Result'] = "No input Packet errors seen on App interface"
    result2['Test Group'] = "KR Port"
    # kr_results.append(result2)

    result3 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['ether-stats']
    result3['Test'] = "App interface output Pause Frames"
    if (intr_stats['out-mac-pause-frames'] != "0"):
        result3['Status'] = "FAIL"
        result3['Result'] = "Output Pause frames have been sent on App interface, error count=" + \
            intr_stats['out-mac-pause-frames']
    else:
        result3['Status'] = "PASS"
        result3['Result'] = "No output Pause frames have been sent on App interface"
    result3['Test Group'] = "KR Port"
    # kr_results.append(result3)

    result4 = {}
    intr_stats = intf_state['data']['interfaces']['interface']['ether-stats']
    result4['Test'] = "Interface input Pause Frames"
    if (intr_stats['in-mac-pause-frames'] != "0"):
        result4['Status'] = "FAIL"
        result4['Result'] = "Input Pause frames have been sent on App interface, error count=" + \
            intr_stats['in-mac-pause-frames']
    else:
        result4['Status'] = "PASS"
        result4['Result'] = "No input Pause frames have been sent on App interface"
    result4['Test Group'] = "KR Port"
    # kr_results.append(result4)


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

    f = open('edge_analytics.html', 'w')
    cgitb.enable()

    # print("Content-Type: text/html")
    # print("")

    # print("<h1>Cat9K switch Overall health</h1>")
    # print("<h2>App-hosting Interface " + intf + " Status</h2>")
    # print("<a href=\"javascript:window.location.reload(true)\">Refresh</a>")
    # print(json2html.convert(json.dumps(intf_state)))

    f.write("<a href=\"javascript:window.location.reload(true)\">Refresh</a>")
    f.write("<h1>Overall switch health</h1>")
    f.write("<h2>App-hosting Interface " + intf + " Status</h2>")

    # summary = summary_table(intf_state)
    # f.write(json2html.convert(json.dumps(summary)))

    filter_results(kr_results, ["Status", "Test Group"])
    f.write(json2html.convert(json.dumps(kr_results)))

    state, stats, _, _ = output_extra(intf_state)
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


def summary(intf_state, ioxInfo, resInfo, appListInfo):
    state, stats, ds, stats_ds = output_extra(intf_state)

    optable = summary_table(intf_state, ioxInfo)
    res_ds = formatAppRes(resInfo)
    iox_ds = formatIoxInfo(ioxInfo)
    appList_ds = formatAppList(appListInfo)

    return {
        "app-resource": res_ds,
        "iox-info": iox_ds,
        "app-list": appList_ds,
        "summary": optable,
        "state": ds,
        "stats": stats_ds}


def get_intf_state():
    intf_state_xml = get_intf_state_data(HOSTNAME, PORT,
                                         USERNAME, PASSWORD,
                                         INTERFACE_NAME)
    intf_state = extract_intf_state(intf_state_xml)
    return intf_state


def connectHost(host, psw, userName=None, returnHostName=False):
    print(host, psw, userName, returnHostName)
    # connect to switch
    while True:
        try:
            tn = telnetlib.Telnet(host, timeout=5)
            break
        except:
            print('failed to connect! retry in 2 sec')
            time.sleep(2)
            pass

    # input username, if any
    if userName is not None:
        tn.read_until("Username: ".encode('ascii'))
        userName += '\n'
        tn.write(userName.encode('ascii'))

    # input password
    password = psw + '\n'
    tn.read_until("Password: ".encode('ascii'))
    tn.write(password.encode('ascii'))

    if userName is None:
        # get host name
        hostName = tn.read_until(">".encode('ascii')).decode().split('\r\n')[
            1].split(">")[0]

        # enable
        tn.write("enable\n".encode('ascii'))
        tn.read_until("Password: ".encode('ascii'))
        tn.write(password.encode('ascii'))
        tn.read_until((hostName + "#").encode('ascii'))
    else:
        # get host name
        hostName = tn.read_until("#".encode('ascii')).decode().split('\r\n')[
            1].split("#")[0]

    # term len 0
    tn.write("term len 0\n".encode('ascii'))
    tn.read_until((hostName + "#").encode('ascii'))

    print("connected!")

    return tn, hostName


# get iox-service info
def readIoxInfo(tn, hostName):
    # sh iox-service
    tn.write("sh iox-service\n".encode('ascii'))
    ioxLog = tn.read_until((hostName + "#").encode('ascii')).decode()
    ioxInfo = dict()
    for info in ioxLog.split('\r\n')[4:]:
        if len(info) < 1:
            break
        ioxInfo[info.split(' : ')[0]] = info.split(' : ')[1].strip()
    return ioxInfo


# check whether iox running
def checkRunning(ioxInfo):
    for i in ioxInfo:
        if ioxInfo[i] == 'Running':
            continue
        else:
            return False
    return True

# get app-hosting list (for future use)


def readAppList(tn, hostName):
    # sh app list
    tn.write("sh app-hosting list\n".encode('ascii'))
    appList = tn.read_until((hostName + "#").encode('ascii')).decode()
    appListInfo = dict()
    if len(appList.split('\r\n')) < 5:
        return appListInfo
    for i in appList.split('\r\n')[3:]:
        if len(i) < 1:
            break
        appListInfo[re.sub(' +', ' ', i).split(' ')[0].strip()
                    ] = re.sub(' +', ' ', i).split(' ')[1].strip()
    return appListInfo


# get app-hosting resource
def readAppRes(tn, hostName):
    # sh app-hosting resource
    tn.write("sh app-hosting resource\n".encode('ascii'))
    appRes = tn.read_until((hostName + "#").encode('ascii')).decode()

    # parse Info
    resInfo = dict()

    cpuQuota = int(appRes.split('\r\n')[2].split(': ')[1].split('(')[0])
    cpuAvail = int(appRes.split('\r\n')[3].split(': ')[1].split('(')[0])

    memQuota = int(appRes.split('\r\n')[5].split(': ')[1].split('(')[0])
    memAvail = int(appRes.split('\r\n')[6].split(': ')[1].split('(')[0])

    storageQuota = int(appRes.split('\r\n')[8].split(': ')[1].split('(')[0])
    storageAvail = int(appRes.split('\r\n')[9].split(': ')[1].split('(')[0])

    resInfo['CPUQuota'] = cpuQuota
    resInfo['CPUAvail'] = cpuAvail
    resInfo['MemoryQuota'] = memQuota
    resInfo['MemoryAvail'] = memAvail
    resInfo['StorageQuota'] = storageQuota
    resInfo['StorageAvail'] = storageAvail

    return resInfo


def get_status(val):
    return "true"


def formatAppRes(resInfo):
    res_ds = []
    for k, v in resInfo.items():
        res_ds.append({
            "key": k,
            "title": res_titles[k],
            "desc": res_descs[k],
            "value": str(v),
            "status": get_status(v)
        })

    return res_ds


def formatIoxInfo(ioxInfo):
    iox_ds = []
    for k, v in ioxInfo.items():
        iox_ds.append({
            "key": k,
            "title": iox_titles[k],
            "desc": iox_descs[k],
            "value": v,
            "status": get_status(v)
        })

    return iox_ds


def formatAppList(appListInfo):
    appList_ds = []
    for k, v in appListInfo.items():
        appList_ds.append({
            "key": k,
            "title": appList_titles[k],
            "desc": appList_descs[k],
            "value": v,
            "status": get_status(v)
        })

    return appList_ds


def formatReadInfo(resInfo, ioxInfo, appListInfo):
    res_ds = formatAppRes(resInfo)
    iox_ds = formatIoxInfo(ioxInfo)
    appList_ds = formatAppList(appListInfo)
    return {
        "app-resource": res_ds,
        "iox-info": iox_ds,
        "app-list": appList_ds
    }


class SwitchInfo(object):
    def __init__(self, host, password, user):
        self.host = host
        self.user = user
        self.password = password

    def connect(self):
        tn, hostName = connectHost(self.host, self.password, self.user)

        self.tn = tn
        self.hostName = hostName

    def resInfo(self):
        return readAppRes(self.tn, self.hostName)

    def ioxInfo(self):
        return readIoxInfo(self.tn, self.hostName)

    def appListInfo(self):
        return readAppList(self.tn, self.hostName)


def getDefaultSwitchInfo():
    return SwitchInfo(HOSTNAME, PASSWORD, USERNAME)


if __name__ == '__main__':
    intf_state = get_intf_state()
    output_summary(intf_state)
    # print(json.dumps(kr_results, indent=2))
    output_intf_state(INTERFACE_NAME, intf_state)

    # connect to switch
    tn, hostName = connectHost(HOSTNAME, PASSWORD, USERNAME)

    resInfo = readAppRes(tn, hostName)
    ioxInfo = readIoxInfo(tn, hostName)
    appListInfo = readAppList(tn, hostName)
    # **remember to close the connection**
    tn.close()

    intf_state_summary = summary(intf_state, ioxInfo, resInfo, appListInfo)
    readInfo = formatReadInfo(resInfo, ioxInfo, appListInfo)
    readInfo.update(intf_state_summary)

    jsonFile = open('edge_analytics.json', 'w')
    jsonFile.write(json.dumps(readInfo))
    jsonFile.close()
    print("edge_analytics.json dumped")
