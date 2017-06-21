#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import subprocess
import logging
import json


# init logging to stnd output and log files
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler()
logger.addHandler(sh)
logger.propagate = True


def launch_sniffer(filename, filter_if, other_filter=None):
    logger.info('Launching packet capture..')

    if other_filter is None:
        other_filter = ''

    if (filter_if is None ) or (filter_if == ''):
        sys_type = platform.system()
        if sys_type == 'Darwin':
            filter_if = 'lo0'
        else:
            filter_if = 'lo'
            # TODO windows?

    # lets try to remove the filename in case there's a previous execution of the TC
    try:
        params = 'rm ' + filename
        os.system(params)
    except:
        pass

    params = 'tcpdump -K -i ' + filter_if + ' -s 200 ' + '  -w ' + filename + ' ' + other_filter + ' &'
    os.system(params)
    logger.info('Creating process tcpdump with: %s' % params)

    # TODO we need to catch tcpdump: <<tun0: No such device exists>> from stderr

    return True


def decode_pcap(filename):

    logger.info('Execute TSHARK to dissect as JSON file')
    json_filename = os.path.splitext(filename)[0] + '.json'

    params = 'tshark -r {0} -l -n -x -T json > {1}'.format(filename, json_filename)
    os.system(params)
    logger.info('Dissect PCAP as JSON using this command: %s' % params)
    return True


def stop_sniffer():
    proc = subprocess.Popen(["pkill", "-INT", "tcpdump"], stdout=subprocess.PIPE)
    proc.wait()
    logger.info('Packet capture stopped')
    return True

def stop_sniffer_with(filename):
    ps_line = os.popen("ps -alx | grep tcpdump | grep [{0}]{1}".format(filename[0], filename[1:])).read()
    if ps_line:
        pid = ps_line.split()[0]
        print(ps_line, pid)
        #proc = subprocess.Popen(["kill", "-INT", pid], stdout=subprocess.PIPE)
        #proc.wait()
        #os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
        logger.info('Packet capture stopped')



def extract_field(pkt, what, msg_type=None):
    try:
        if what == 'frame_id':
            return pkt["_source"]['layers']['frame']['frame.number']
        elif what == 'time_epoch':
            return pkt["_source"]['layers']['frame']['frame.time_epoch']
        elif what == 'time_delta_displayed':
            return pkt["_source"]['layers']['frame']['frame.time_delta_displayed']
        elif what == 'frame_size':
            return pkt["_source"]['layers']['frame']['frame.len']
        elif what == 'time_delta':
            return pkt["_source"]['layers']['frame']['frame.time_delta']
        elif what == 'mqtt_type':
            return pkt["_source"]['layers']['mqtt'].keys()[0]
        elif what == 'mqtt_size':
            return pkt["_source"]['layers']['mqtt'][msg_type]['mqtt.len']
        elif what == 'mqtt_id':
            if 'mqtt.msgid' in pkt["_source"]['layers']['mqtt'][msg_type]:
                return pkt["_source"]['layers']['mqtt'][msg_type]['mqtt.msgid']
            else:
                return "NA"
        elif what == 'udp_size':
            return pkt["_source"]['layers']['udp']['udp.length']
        elif what == 'tcp_size':
            return pkt["_source"]['layers']['tcp']['tcp.len']
        elif what == 'protocols':
            return pkt["_source"]['layers']['frame']['frame.protocols']
        else:
            print ("%s is not a valida parameter" % what)
            raise Exception("{0} is not a valid parameter".format(what))
    except:
        logger.error("Error while parsing json conversation")
        raise Exception("Error while parsing json conversation")
