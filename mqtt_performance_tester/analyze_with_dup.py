from mqtt_performance_tester.data_types import mqtt_e2e
from mqtt_performance_tester.mqtt_utils import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
            elif 'mqtt.msg' in l:
                pkt.body = l
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

                    # logger.debug("- MQTT n.{0} {1}".format(self.mqtt_counter, repr(pkt)))
                    # if pkt.type == MQTT_DISCONNECT:
                    #     logger.debug(" ------------- ")

                    self.mqtt_payload_size += pkt.payload_size
                    self.mqtt_tcp_size     += pkt.protocol_size
                    self.packets.append(pkt)

                    # to compute the E2E
                    if pkt.type == MQTT_PUB:
                        self.pubMessage.append(pkt)
                    elif pkt.type == MQTT_PUB_ACK or pkt.type == MQTT_PUB_COM:
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

        logger.debug('---------------------------------------')
        logger.debug("Detected %d MQTT packets" % len(self.packets))
        logger.debug('---------------------------------------')
        for key in self.count_mqtt_type.keys():
            logger.debug('--- n. {1} of MQTT msg: {0}  '.format(key, self.count_mqtt_type[key]))
        logger.debug('---------------------------------------')
        logger.debug("--- %d TOTAL MQTT msg exchanged " % (self.num_mqtt))
        logger.debug('---------------------------------------')
        logger.debug('--- Total Message:       %d'   % self.counter)
        logger.debug("--- N.Frames:            %s "     % self.frames_num)
        logger.debug("--- TCP Message:         %s "    % self.num_tcp)
        logger.debug('--- MQTT Message:        %d'    % self.num_mqtt)
        logger.debug('--- UDP Message:         %d'     % self.num_upd)
        logger.debug('--- OTHER Message:       %d'   % self.num_others)
        logger.debug('---------------------------------------')
        logger.debug('--- TCP  packets size:   %d'   % self.size_tcp)
        logger.debug('--- MQTT TCP size:       %d' % self.mqtt_tcp_size)
        logger.debug('--- TCP + TCP:MQTT size: %d' % (self.size_tcp + self.mqtt_tcp_size))
        logger.debug('--- MQTT payload size:   %d' % self.mqtt_payload_size)
        logger.debug('--- UPD packets size:    %d'    % self.size_udp)
        logger.debug('--- OTHERS packets size: %d' % self.size_others)
        logger.debug('--- TCP+UDP+OTHER size:  %d'  % ( self.size_tcp + self.size_udp + self.size_others+ self.mqtt_tcp_size))
        logger.debug('--- TOTAL Frames size:   %d'   % self.frames_size)
        logger.debug('---------------------------------------')


    def get_sequence(self):

        for p in self.packets:
            logger.debug ("{0} {1} {2}".format(p.mid, p.type, p.payload_size))


    def get_size(self, protocol):
        if protocol == TCP:
            return self.size_tcp
        elif protocol == MQTT:
            return self.size_mqtt
        else:
            return 0


    def get_packet_drop(self):

        size  = self.size_tcp + self.mqtt_tcp_size
        if float(size) == 0:
            return 0
        pdrop = (self.mqtt_payload_size * 1.0) / float(size)
        logger.info("[Packet  DROP] MQTT_PAYLOAD[%d] / TCP+MQTT_TCP[%d]= %f " % (self.mqtt_payload_size, size,pdrop))
        return float("{0:.2f}".format(pdrop*100))


    def get_tcp_overhead(self):
        size = self.size_tcp + self.mqtt_tcp_size

        if float(size) == 0:
            return 0

        overhead_tcp = (self.size_tcp*1.0)/size
        overhead_mqtt = (self.mqtt_payload_size * 1.0) / size
        logger.info("[TCP_OVERHEAD] TCP [%d] / TOTAL (TCP+MQTT)[%d] = %f " % (self.size_tcp, size, overhead_tcp))
        logger.info("[TCP_OVERHEAD] MQTT[%d] / TOTAL (TCP+MQTT)[%d] = %f " % (self.mqtt_payload_size, size, overhead_mqtt))
        return float("{0:.2f}".format(overhead_tcp*100)), float("{0:.2f}".format(overhead_mqtt*100))



def computeTime(json_file, num_test, qos):

    with open(json_file) as file:
        content = str(file.readlines())
        file.close()

    lines = content.replace("', '", "").split("\\n")

    return mqtt_performance(lines, num_test, qos)




def compute_e2e_latency(pkts):

    values = []
    e2e = 0
    wait_ack = True
    sequence = []

    for p in pkts:
        sequence.append(p.type)
        logger.debug("{0} with MID: {1} - time {2}".format(p.type, p.mid, p.epoc_time))
        if p.type == MQTT_PUB:
            if wait_ack:
                logger.warning("[-] Retransmission of Pub ")
                logger.warning(repr(p))
            e2e = p.epoc_time
            wait_ack = True
        elif p.type == MQTT_PUB_ACK or p.type == MQTT_PUB_COM:
            if wait_ack:
                values.append (float(p.epoc_time - e2e))
                logger.warning("[-] Message completed in {}".format(p.epoc_time - e2e))
                wait_ack = False
                # logger.warning("[-] Sequence: {}".format("| -> |".join(sequence)))
                # sequence = []
            # else:
            #     logger.warning("[-] Duplicate ACK")



    logger.info("[E2E Latency]  MIN: {0} AVG:{1} MAX:{2}".format(min(values), sum(values)*0.1/len(values), max(values)))
    return min(values), sum(values)*0.1/len(values), max(values), values



if __name__ == '__main__':
    logger.debug('#######################################################')
    logger.debug("#")
    logger.debug("# Analyze Wireshark data for MQTT Performance analysis")
    logger.debug("#")
    logger.debug('#######################################################')

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    LOG_FORMAT = '%(levelname)-7s | %(asctime)s | %(message)s'
    formatter = logging.Formatter(LOG_FORMAT)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    json_file = "all_sim/data_500_mqtt_with_70%_off/mqtt_capture_qos_1_payload_1280_num_req_500.json"

    demo = computeTime(json_file, 500, 1)
    logger.debug("============== STATS ==============")
    compute_e2e_latency(demo.packets)
    demo.get_packet_drop()
    demo.get_tcp_overhead()
