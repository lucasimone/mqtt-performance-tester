#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from mqtt_performance_tester.data_types import packet

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Message Types
TCP              = "TCP"
MQTT             = "MQTT"
MQTT_SUB_REQ     = "Subscribe Request"
MQTT_SUB_ACK     = "Subscribe Ack"
MQTT_CON_CMD     = 'Connect Command'
MQTT_PUB_ACK     = 'Publish Ack'
MQTT_PUB         = 'Publish Message'
MQTT_PUB_REL     = 'Publish Release'
MQTT_PUB_REC     = 'Publish Received'
MQTT_PUB_COM     = 'Publish Complete'
MQTT_CON_ACK     = 'Connect Ack'
MQTT_CON         = 'Connect Message'
MQTT_PING_REQ    = 'Ping Request'
MQTT_PING_RES    = 'Ping Response'
MQTT_DISCONNECT  =  "Disconnect Req"
MQTT_TCP_SPUR    = '[TCP Spurious'


mqtt_msg_type = [    ## Publish
                     MQTT_PUB,
                     MQTT_PUB_ACK,
                     MQTT_PUB_REC,
                     MQTT_PUB_COM,
                     ## Connect
                     MQTT_CON,
                     MQTT_CON_ACK,
                     MQTT_CON_CMD,
                     ## Ping
                     MQTT_PING_REQ,
                     MQTT_PING_RES,
                     ## SUBSCRIBE
                     MQTT_SUB_ACK,
                     MQTT_SUB_REQ,
                     ## TCP SPURIOUS
                     MQTT_TCP_SPUR
                    ]


# This function read the JSON conversion of the PCAP File
# and extract certain fields
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