import logging

from mqtt_performance_tester.mqtt_utils import packet
from mqtt_performance_tester import N_PACKET_SEND, QoS
from mqtt_performance_tester.data_types import mqtt_e2e


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
### CLASS FOR COMPUTE ALL THE PERFORMANCE PARAMS

class mqtt_performance():


    def __init__(self, data, num_request, qos=1):
        self.num_request = num_request
        self.qos = qos
        self.data = data
        self.packets = []
        self.size_tcp = 0
        self.mqtt_payload_size = 0
        self.mqtt_tcp_size = 0
        self.size_udp = 0
        self.size_others = 0
        self.counter = 0
        self.num_mqtt = 0
        self.num_tcp = 0
        self.num_upd = 0
        self.num_others = 0
        self.frames_size = 0
        self.frames_num = 0
        self.mqtt_types = []
        self.mqtt_ids   = []
        self.count_mqtt_type = dict()

        self.mid_duplicated = False
        self.pubMessage = []
        self.pubAck     = []

        # DO THINGS
        self._parse_data()
        self.print_report()

    def get(self, data):
        return data.split()[1].replace('"', "")

    def getInt(self, data):
        val = self.get(data)
        return int(val.replace(",", ""))

    def getFloat(self, data):
        val = self.get(data)
        return float(val.replace(",", ""))

    def _parse_data(self):

        logger.debug("Search data in {0} line of strings".format(len(self.data)))

        self.counter = 0
        self.mqtt_counter = 0
        pkt = None
        for index, l in enumerate(self.data):
            if "_index" in l:
                self.counter += 1
                self.add_packet(pkt)
                pkt = packet()

            elif "frame.protocols" in l:
                pkt.protocol = self.get(l)
            elif '"mqtt.msgid"' in l:
                if pkt.mid > -1:
                    logger.debug("INCAPSULATION...")
                    self.add_packet(pkt)
                    tmp = packet()
                    tmp.frame_id = pkt.frame_id
                    tmp.protocol = pkt.protocol
                    tmp.protocol_size = pkt.protocol_size
                    tmp.payload_size  = pkt.payload_size
                    tmp.frame_size = pkt.frame_size
                    tmp.type = pkt.type
                    tmp.epoc_time = pkt.epoc_time
                    pkt = tmp
                    #pkt = packet.copy(pkt)

                pkt.mid = self.getInt(l)
                if pkt.mid not in self.mqtt_ids:
                    self.mqtt_ids.append(pkt.mid)
                else:
                    self.mid_duplicated = True

            elif 'mqtt.len":' in l:
                pkt.payload_size = self.getInt(l)
            elif "frame.time_epoch" in l:
                pkt.epoc_time = self.getFloat(l)
            elif '"tcp.len":' in l:
                 pkt.protocol_size = self.getInt(l)
            elif "frame.time_delta_displayed" in l:
                pkt.delta_time = self.getFloat(l)
            elif 'udp.length":' in l:
                pkt.protocol_size = self.getInt(l)
            elif "frame.number" in l:
                pkt.frame_id =self.getInt(l)
            elif "frame.len" in l:
                self.frames_size += self.getInt(l)
                self.frames_num += 1
            elif '"mqtt": {' in l:
                pkt.type = self.data[index + 1].split('"')[1]
                if pkt.type in self.count_mqtt_type:
                    self.count_mqtt_type[pkt.type] += 1
                else:
                    self.count_mqtt_type[pkt.type] = 1

        self.add_packet(pkt)



    def add_packet(self, pkt):
        if pkt:
            if pkt.protocol:
                if "mqtt" in pkt.protocol:
                    self.mqtt_counter += 1
                    if pkt.mid not in self.mqtt_ids:
                        self.mqtt_ids.append(pkt.mid)
                    self.num_mqtt += 1
                    logger.debug("- MQTT n.{0}{1}".format(self.mqtt_counter, repr(pkt)))
                    self.mqtt_payload_size += pkt.payload_size
                    self.mqtt_tcp_size     += pkt.protocol_size
                    self.packets.append(pkt)

                    # to compute the E2E
                    if pkt.type == self.MQTT_PUB:
                        self.pubMessage.append(pkt)
                    elif pkt.type == self.MQTT_PUB_ACK or pkt.type == self.MQTT_PUB_COM:
                        self.pubAck.append(pkt)

                elif "tcp" in pkt.protocol:
                    self.num_tcp += 1
                    self.size_tcp += pkt.protocol_size
                    pkt.type = "TCP"
                    #logger.debug("---- TCP -n.{0} {1}".format(self.num_tcp, repr(pkt)))
                elif "upd" in pkt.protocol:
                    self.num_upd += 1
                    self.size_udp += pkt.protocol_size
                    pkt.type = "UDP"
                    #logger.debug("---- UPD -n.{0} {1}".format(self.num_upd, repr(pkt)))
                else:
                    self.size_others += pkt.protocol_size
                    self.num_others += 1
                    pkt.type = "???"
                    #logger.debug("---- OTHER -n.{0} {1}".format(self.num_others, repr(pkt)))


            else:
                self.num_others += 1
                self.size_others += pkt.protocol_size
                #logger.debug("---- OTHER -n.{0} {1}".format(self.num_others, repr(pkt)))


    def print_report(self):

        print ("\n\n")
        logger.debug("Detected %d MQTT packets" % len(self.packets))
        logger.debug('#######################################')
        for key in self.count_mqtt_type.keys():
            logger.debug('--- n. {1} of MQTT msg: {0}  '.format(key, self.count_mqtt_type[key]))
        logger.debug('---------------------------------------')
        logger.debug("--- %d TOTAL MQTT msg exchanged " % (self.num_mqtt))
        logger.debug('---------------------------------------')
        logger.debug("--- QoS %d " % (self.qos))
        logger.debug("--- DUP IDs {0}".format(self.mid_duplicated))
        #logger.debug("IDS: ", self.mqtt_ids)
        logger.debug('#######################################')
        logger.debug('--- Total Message:       %d'   % self.counter)
        logger.debug("--- N.Frames:            %s "     % self.frames_num)
        logger.debug("--- TCP Message:         %s "    % self.num_tcp)
        logger.debug('--- MQTT Message:        %d'    % self.num_mqtt)
        logger.debug('--- UDP Message:         %d'     % self.num_upd)
        logger.debug('--- OTHER Message:       %d'   % self.num_others)
        logger.debug('#######################################')
        logger.debug('--- TCP  packets size:   %d'   % self.size_tcp)
        logger.debug('--- MQTT TCP size:       %d' % self.mqtt_tcp_size)
        logger.debug('--- TCP + TCP:MQTT size: %d' % (self.size_tcp + self.mqtt_tcp_size))
        logger.debug('--- MQTT payload size:   %d' % self.mqtt_payload_size)
        logger.debug('--- UPD packets size:    %d'    % self.size_udp)
        logger.debug('--- OTHERS packets size: %d' % self.size_others)
        logger.debug('--- TCP+UDP+OTHER size:  %d'  % ( self.size_tcp + self.size_udp + self.size_others+ self.mqtt_tcp_size))
        logger.debug('--- TOTAL Frames size:   %d'   % self.frames_size)
        logger.debug('#######################################')


    def all_ack_received(self):
        sequence = dict()

        for pkt in self.packets:
            if pkt.mid not in sequence:
                sequence[pkt.mid] = 0
            if pkt.type == self.MQTT_PUB:
                sequence[pkt.mid] += 1
            elif pkt.type == self.MQTT_PUB_ACK or pkt.type == self.MQTT_PUB_REL:
                sequence[pkt.mid] -= 1


        logger.debug ("Received {0}/{1} ACK) ".format(len(sequence.keys(), self.num_request)))
        logger.debug ("Missing ACK = {0}".format(sum(sequence.values())))
        return len(sequence.keys()) == self.num_request




    def get_e2e_random_sequence(self):
        sequence = dict()

        for pkt in self.packets:
            if pkt.mid not in sequence and pkt.mid != -1:
                sequence[pkt.mid] = mqtt_e2e()
            if pkt.mid != -1:
                sequence[pkt.mid].add(pkt)

        values = []
        for p in sequence.values():
            values.append(p.get_latency())

        return min(values), max(values), sum(values)/len(values)


    def print_packets(self):

        sequence = dict()

        for pkt in self.packets:
            if pkt.mid not in sequence and pkt.mid != -1:
                sequence[pkt.mid] = mqtt_e2e()
            if pkt.mid != -1:
                sequence[pkt.mid].add(pkt)

        for p in sequence.values():
            #print("MID:{0} Publish:{1} ACK:{2} e2e:{3}".format(p.get_mid(), p.get_publish(), p.get_ack(), p.get_latency()))
            logger.debug (repr(p))

        logger.debug (" Send n. {0} differnt MID".format(len(sequence)))

    def get_num(self, msg_type):
        return len(self.filter_by(msg_type))

    def filter_by(self, filter):
        output = []
        for pkt in self.packets:
            if pkt.type == filter:
                output.append(pkt)
                #print("+++ add {0} {1}".format(pkt.mid, pkt.type))
            #else:
                #print ("skip {0}".format(pkt.type))

        return output

    def find_msg_with_id(self, mid, msg_type):
        data = self.filter_by(msg_type)
        for msg in data:
            if msg.mid == mid:
                return msg
        return -1


    def get_sequence(self):

        for p in self.packets:
            logger.debug ("{0} {1} {2}".format(p.mid, p.type, p.payload_size))


    def get_new_e2e(self):

        pub_id = [x.mid for x in self.pubMessage]
        ack_id = [y.mid for y in self.pubAck]
        logger.debug ("PUB IDs:", pub_id)
        logger.debug ("ACK IDs:", ack_id)
        values = []
        for index, p in enumerate(self.pubMessage):
            ack = self.pubAck[index]
            if ack.mid == p.mid:
                e2e = ack.epoc_time - p.epoc_time
                values.append(e2e)
            else:
                logger.debug("{0} - {1}  - {2}".format(index, p.mid, ack.mid))

        logger.debug("E2E MIN={0} - MAX={1} -  AVG={2}".format(min(values), max(values), sum(values)/len(self.pubAck)))
        return min(values), max(values), sum(values)/len(self.pubAck)

    def get_e2e(self):

        min = 100000
        max = -1
        msg_type = self.MQTT_PUB_ACK
        if self.qos == 2:
            msg_type = self.MQTT_PUB_COM

        avg_time = 0
        counter  = 0
        data = self.filter_by(msg_type)

        for msg in data:
            msg_pub = self.find_msg_with_id(msg.mid, self.MQTT_PUB)

            mqtt_time  = (float(msg.epoc_time) - float(msg_pub.epoc_time))
            logger.debug("{0}[{5}]:{1} - {2}[{6}]:{3} = {4}".format(msg_type,msg.epoc_time,  self.MQTT_PUB, msg_pub.epoc_time, mqtt_time, msg.mid, msg_pub.mid))
            if mqtt_time > max:
                max = mqtt_time
            if mqtt_time < min:
                min = mqtt_time
            avg_time += mqtt_time
            #print ("%s -- %s " % (repr(msg), repr(msg_pub)))
            counter += 1

        logger.debug("[E2E] TOTAL TIME: %s " % avg_time)
        if counter == 0:
            avg_time = 0
        else:
            avg_time /= counter
        logger.debug("[E2E] MIN TIME: %s - MAX TIME: %s" % (min, max))

        logger.debug("[E2E] The E2E delay for %s is :%f [N. Pkt=%d]" %(msg_type, avg_time, counter))
        return avg_time


    def get_pdr(self):

        pub = 0
        ack = 0
        sequence = dict()
        for pkt in self.packets:
            if pkt.mid not in sequence and pkt.mid != -1:
                sequence[pkt.mid] = mqtt_e2e()
            if pkt.mid != -1:
                sequence[pkt.mid].add(pkt)
                if pkt.type == self.MQTT_PUB:
                    pub += 1
                else:
                    ack += 1

        #
        #
        #
        # counter = len(self.pubAck)
        #pdr = (counter *1.0 / len(self.pubMessage)) * 100
        pdr = (ack * 1.0 / pub) * 100
        #print("[Packet Delivery Ratio] ACK[%d] / PUB[%d] = %f [REQUEST sent: %d]" % (len(self.pubAck), len(self.pubMessage), pdr, N_PACKET_SEND))
        logger.debug("[Packet Delivery Ratio] ACK[%d] / PUB[%d] = %f [REQUEST sent: %d]" % (ack, pub, pdr, N_PACKET_SEND))
        return pdr

    def get_size(self, protocol):
        if protocol == self.TCP:
            return self.size_tcp
        elif protocol == self.MQTT:
            return self.size_mqtt
        else:
            return 0



    def get_packet_drop(self):

        # if self.qos == 1:
        #     num_ack = self.get_num(self.MQTT_PUB_ACK)
        #     ack_type = self.MQTT_PUB_ACK
        # else:
        #     num_ack = self.get_num(self.MQTT_PUB_COM)
        #     ack_type = self.MQTT_PUB_COM
        # num_ack = len(self.pubAck)

        size  = self.size_tcp + self.mqtt_tcp_size

        if float(size) == 0:
            return 0

        pdrop = (self.mqtt_payload_size * 1.0) / float(size)
        logger.debug("[Packet  DROP] MQTT_PAYLOAD[%d] / TCP+MQTT_TCP[%d]= %f " % (self.mqtt_payload_size, size,pdrop))
        return pdrop


    def get_tcp_overhead(self):
        size = self.size_tcp + self.mqtt_tcp_size

        if float(size) == 0:
            return 0

        overhead_tcp = (self.size_tcp*1.0)/size
        overhead_mqtt = (self.mqtt_payload_size * 1.0) / size
        logger.debug("[TCP_OVERHEAD] TCP [%d] / TOTAL (TCP+MQTT)[%d] = %f " % (self.size_tcp, size, overhead_tcp))
        logger.debug("[TCP_OVERHEAD] MQTT[%d] / TOTAL (TCP+MQTT)[%d] = %f " % (self.mqtt_payload_size, size, overhead_mqtt))
        return overhead_tcp, overhead_mqtt



def computeTime(json_file, num_test, qos):

    with open(json_file) as file:
        content = str(file.readlines())
        file.close()

    lines = content.replace("', '", "").split("\\n")

    return mqtt_performance(lines, num_test, qos)





if __name__ == '__main__':
    logger.debug('#######################################################')
    logger.debug("#")
    logger.debug("# Analyze Wireshark data for MQTT Performance analysis")
    logger.debug("#")
    logger.debug('#######################################################')

    json_file = "../data/mqtt_capture_qos_1_payload_128.json"

    demo = computeTime(json_file, N_PACKET_SEND, QoS[0])
    logger.debug(demo.get_e2e_random_sequence())
    #demo.get_new_e2e()
    #demo.get_pdr()
    #demo.get_packet_drop()
    #demo.get_tcp_overhead()
