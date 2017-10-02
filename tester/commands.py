#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import subprocess
import logging
import time
from tester import GW_IP



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

    #params = 'tcpdump -i ' + filter_if  + ' ' + other_filter + ' -vv -w ' + filename + ' &'
    params = 'tcpdump -i %s -vv %s -w %s &' % (filter_if, other_filter, filename)
    logger.info('Creating process TCPDUMP with: %s' % params)
    os.system(params)

    # TODO we need to catch tcpdump: <<tun0: No such device exists>> from stderr

    return True


def decode_pcap(filename):

    #logger.info('Execute TSHARK to dissect as JSON file')
    json_filename = os.path.splitext(filename)[0] + '.json'

    params = 'tshark -r {0} -l -n -x -T json > {1}'.format(filename, json_filename)


    os.system(params)
    #logger.info('Dissect PCAP as JSON using this command: %s' % params)
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
        print(ps_line, pid)
        #proc = subprocess.Popen(["kill", "-INT", pid], stdout=subprocess.PIPE)
        #proc.wait()
        #os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
        logger.info('Packet capture stopped')


def check_end_of_transmission(filename, qos, num):

    while not os.path.exists(filename):
        time.sleep(0.001)
    print("PCAP file has been created ...")

    while os.path.getsize(filename) < 24:
        pass
    print("PCAP contains at lease 1 packet")

    wait_first_ping_to_quit = True
    while wait_first_ping_to_quit :

        decode_pcap(filename)  # GEN JSON FILE
        json_filename = os.path.splitext(filename)[0] + '.json'


        check_message  = "Publish Ack"
        if qos == 2:
            check_message = "Publish Release"

        packets = read_json_partial_pcap(json_filename)

        #process = subprocess.Popen(['grep', check_message, json_filename], stdout=subprocess.PIPE)
        #ping_out, ping_err = process.communicate()

        num_ack = get_num_ids(packets, check_message)
        if  num_ack >= num:
            wait_first_ping_to_quit = False
            print("GET {0} Message type {1} --- STOP SNIFFER....".format(num, check_message))
        else:
            print("Received ACK {0}/{1}".format(num_ack, num))
            # I need to send some data after the transmission is finished because TCP dumpo
            # does not store packtes until it gets a certain amount of data
            print ("ping -c 2 -s 512 {0}".format(GW_IP))
            os.system("ping -c 2 -s 512 {0}".format(GW_IP))



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
            return list(pkt["_source"]['layers']['mqtt'].keys())[0]
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



### CLASS FOR STORE AN MQTT MESSAGE
class packet():

    counter = 0

    def __init__(self):
        self.protocol = None
        self.frame_id = None
        self.type = None
        self.protocol_size = 0
        self.payload_size = 0
        self.frame_size = 0
        self.delta_time = -1
        self.epoc_time = -1
        self.qos = -1
        self.mid = -1


    def copy(tmp):
        pkt = packet()
        pkt.protocol_size = tmp.protocol
        pkt.frame_id = tmp.protocol
        pkt.type = tmp.type
        pkt.protocol_size = tmp.protocol_size
        pkt.payload_size = tmp.payload_size
        pkt.frame_size = tmp.frame_size
        pkt.delta_time =  tmp.delta_time
        pkt.epoc_time = tmp.epoc_time
        pkt.qos = tmp.qos
        pkt.mid = tmp.mid
        return pkt



    def __repr__(self):
        return "---FRAME[%s] mid:%s \t%s \tType:%s \tFrame|Protocol|Payload Size:%s|%s|%s \tTime:%s \tEpoc:%s" \
               %(self.frame_id, self.mid, self.protocol, self.type, self.frame_size, self.protocol_size,
                 self.payload_size, self.delta_time, self.epoc_time)





# Read JSON FILE and get all packets

def read_json_partial_pcap(json_file):


    with open(json_file) as file:
        content = str(file.readlines())
        file.close()

    data = content.replace("', '", "").split("\\n")

    def get(elm):
        return elm.split()[1].replace('"', "")

    def getInt(elm):
        val = get(elm)
        return int(val.replace(",", ""))

    def getFloat(elm):
        val = get(elm)
        return float(val.replace(",", ""))

    packets = []
    pkt = None
    for index, l in enumerate(data):
        if "_index" in l:
            if pkt:
                packets.append(pkt)
            pkt = packet()
        elif "frame.protocols" in l:
            pkt.protocol = get(l)

        elif '"mqtt.msgid"' in l:
            if pkt.mid > -1:
                packets.append(pkt)
                tmp = packet()
                tmp.frame_id = pkt.frame_id
                tmp.protocol = pkt.protocol
                tmp.protocol_size = pkt.protocol_size
                tmp.payload_size  = pkt.payload_size
                tmp.frame_size = pkt.frame_size
                tmp.type = pkt.type
                tmp.epoc_time = pkt.epoc_time
                pkt = tmp
            pkt.mid = getInt(l)

        elif 'mqtt.len":' in l:
                pkt.payload_size = getInt(l)
        elif "frame.time_epoch" in l:
                pkt.epoc_time = getFloat(l)
        elif '"tcp.len":' in l:
                 pkt.protocol_size = getInt(l)
        elif "frame.time_delta_displayed" in l:
                pkt.delta_time = getFloat(l)
        elif 'udp.length":' in l:
                pkt.protocol_size = getInt(l)
        elif "frame.number" in l:
                pkt.frame_id = getInt(l)
        elif '"mqtt": {' in l:
                pkt.type = data[index + 1].split('"')[1]

    if "mqtt" in pkt.protocol:
        packets.append(pkt)

    return packets



def get_num_ids(pkts, mtype=None):

    ids=[]
    for p in pkts:
        if p.mid not in ids and p.mid != -1:
            if mtype:
                if p.type == mtype:
                    ids.append(p.mid)
            else:
                ids.append(p.mid)
    return len(ids)

if __name__ == '__main__':


    print ("check read JSON_PCAP")
    json_file = "..//mqtt_capture_qos_1_payload_1024.json"
    print (json_file)
    pkts = read_json_partial_pcap(json_file)

    print (get_num_ids(pkts, mtype='Publish Ack'))
