#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import platform
import os
import subprocess
import time



from mqtt_performance_tester.mqtt_utils import read_json_partial_pcap
from mqtt_performance_tester.mqtt_utils import get_num_ids

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_paylod(size, num, qos):
    payload = "[START PAYLOAD][MSG_N:{1} SIZE_BYTE:{0} QOS:{2}][".format(size, num+1, qos)
    stop = "][END PAYLOAD N.{0}]".format(num+1)
    num_char = size - len(payload) - len(stop)
    for i in range(num_char):
        payload += "0"
    payload += stop
    return payload


def start_mqtt_client(qos, payload_size, num, topic, host):

    for count in range(num):
        params = "mosquitto_pub -d -h %s -q %d -t %s -m '%s'" % (host, qos, "%s-%d"%(topic, qos), create_paylod(payload_size, count, qos))
        logger.debug(" >>> Sending packet n.%d/%s with Payload: %s" %(count+1, num, payload_size))
        os.system(params)


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

    #params = 'tcpdump -i ' + filter_if  + ' ' + other_filter + ' -vv -w ' + filename + ' &'
    params = 'tcpdump -i %s -vv %s -w %s &' % (filter_if, other_filter, filename)
    logger.info('Creating process TCPDUMP with: %s' % params)
    os.system(params)

    # TODO we need to catch tcpdump: <<tun0: No such device exists>> from stderr

    return True


def decode_pcap(filename):

    logger.debug('Execute TSHARK to dissect as JSON file')
    json_filename = os.path.splitext(filename)[0] + '.json'
    params = 'tshark -r {0} -l -n -x -T json > {1}'.format(filename, json_filename)
    os.system(params)
    logger.debug('Dissect PCAP as JSON using this command: %s' % params)
    return True


def stop_sniffer():
    proc = subprocess.Popen(["pkill", "-INT", "tcpdump"], stdout=subprocess.PIPE)
    proc.wait()
    logger.info('Packet capture stopped')

    return True

def show_pcap(filename):
    logger.info("SHOW: tcpdump -s 0 -n -e -x -vvv -r %s" %filename)
    os.system("tcpdump -s 0 -n -e -x -vvv -r %s" %filename)


def stop_sniffer_with(filename):
    ps_line = os.popen("ps -alx | grep tcpdump | grep [{0}]{1}".format(filename[0], filename[1:])).read()
    if ps_line:
        pid = ps_line.split()[0]
        logger.debug(ps_line, pid)
        #proc = subprocess.Popen(["kill", "-INT", pid], stdout=subprocess.PIPE)
        #proc.wait()
        #os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
        logger.info('Packet capture stopped')


def check_end_of_transmission(filename, qos, num, host):

    while not os.path.exists(filename):
        time.sleep(0.001)
    logger.debug("PCAP file has been created ...")

    while os.path.getsize(filename) < 24:
        pass
    logger.debug("PCAP contains at lease 1 packet")

    wait_first_ping_to_quit = True
    while wait_first_ping_to_quit :

        decode_pcap(filename)  # GEN JSON FILE
        json_filename = os.path.splitext(filename)[0] + '.json'
        check_message  = "Publish Ack"
        if qos == 2:
            check_message = "Publish Release"

        packets = read_json_partial_pcap(json_filename)

        # process = subprocess.Popen(['grep', check_message, json_filename], stdout=subprocess.PIPE)
        # ping_out, ping_err = process.communicate()

        num_ack = get_num_ids(packets, check_message)
        if  num_ack >= num:
            wait_first_ping_to_quit = False
            logger.debug("GET {0} Message type {1} --- STOP SNIFFER....".format(num, check_message))
        else:
            logger.debug("Received ACK {0}/{1}".format(num_ack, num))
            # I need to send some data after the transmission is finished because TCP dumpo
            # does not store packtes until it gets a certain amount of data
            logger.debug ("ping -c 2 -s 512 {0}".format(host))
            os.system("ping -c 2 -s 512 {0}".format(host))



if __name__ == '__main__':


    logger.info ("check read JSON_PCAP")
    json_file = "..//mqtt_capture_qos_1_payload_1024.json"
    logger.info (json_file)
    pkts = read_json_partial_pcap(json_file)

    logger.info (get_num_ids(pkts, mtype='Publish Ack'))
