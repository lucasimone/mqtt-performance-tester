#!/usr/bin/env python
# -*- coding: utf-8 -*


'''
CLASS FOR STORE AN MQTT MESSAGE
'''

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



class mqtt_e2e():

    def __init__(self):
        self.publish = []
        self.ack = []
        self.pkts = []
        self.mid = 0


    def get_ack(self):
        return len(self.ack)

    def get_publish(self):
        return len(self.publish)

    def get_mid(self):
        return self.mid

    def get_latency(self):
        if len(self.ack) > 0 :
            ack = self.ack[0]
        else:
            ack = 0

        if len(self.publish) > 0:
            pm = self.publish[0]
        else:
            pm = 0
        return ack - pm

    def add(self, pkt):
        self.mid = pkt.mid
        self.pkts.append(pkt)
        if pkt.type == "Publish Message":
            self.publish.append(pkt.epoc_time)
        else:
            self.ack.append(pkt.epoc_time)

    def __repr__(self):
        return "MID: %s  [%s] PM %s - ACK %s - latency %s" %(self.mid, " \n".join([x.type for x in self.pkts]), len(self.publish), len(self.ack), self.get_latency())


