import json
from tester.commands import extract_field

### CLASS FOR STORE AN MQTT MESSAGE
class packet():

    counter = 0


    def __init__(self):
        self.protocol = None
        self.frame_id = None
        self.type = None
        self.size = -1
        self.delta_time = -1
        self.epoc_time = -1
        self.mid = -1


    def __repr__(self):
        return "%s Type:%s mid:%s Size:%s - Time:%s Epoc:%s" \
               %(self.protocol, self.type, self.mid, self.size, self.delta_time, self.epoc_time)


### CLASS FOR COMPUTE ALL THE PERFORMANCE PARAMS

class mqtt_performance():

    TCP             = "TCP"
    MQTT            = "MQTT"
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
    MQTT_TCP_SPUR    = '[TCP Spurious'

    mqtt_msg_type = [## Publish
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

    def __init__(self, data, num_request, qos=1):
        self.num_request = num_request
        self.qos = qos
        self.data = data
        self.packets = []
        self.size_tcp = 0
        self.size_mqtt = 0
        self.size_udp = 0
        self.size_others = 0
        self.counter = 0
        self.num_mqtt = 0
        self.num_tcp = 0
        self.num_upd = 0
        self.num_others = 0
        self.mqtt_types = []

        self._parse_json()


    def _parse_json(self):

        self.counter = 0
        index = 0  # start_counter
        msg = None
        for pkt in self.data:
                msg = packet()
                try:

                    msg.frame_id = extract_field(pkt, 'frame_id')

                    # Read TIME
                    msg.delta_time = extract_field(pkt, "time_delta")
                    msg.epoc_time = extract_field(pkt, "time_epoch")
                    if 'mqtt' in pkt["_source"]['layers']:
                        self.counter += 1
                        msg.type = extract_field(pkt, "mqtt_type")
                        msg.size = extract_field(pkt, "mqtt_size", msg.type)
                        msg.mid  = extract_field(pkt, "mqtt_id",   msg.type)
                        msg.protocol = "mqtt"

                        if msg.type not in self.mqtt_types:
                            self.mqtt_types.append(msg.type)
                        self.num_mqtt += 1
                        self.size_mqtt += int(msg.size)
                        self.packets.append(msg)

                    elif 'udp' in pkt["_source"]['layers']:
                        msg.protocol = "udp"
                        msg.size = extract_field(pkt, "udp_size")
                        self.size_udp += int(msg.size)
                        self.num_upd += 1
                    elif 'tcp' in pkt["_source"]['layers']:
                        msg.protocol = "tcp"
                        msg.size = int(extract_field(pkt, "tcp_size"))
                        self.size_tcp += int(msg.size)
                        self.num_tcp += 1
                    else:
                        msg.protocol = extract_field(pkt, "protocols")
                        #print ("protocols: " + msg.protocol)
                        msg.size = extract_field(pkt, "frame_size")
                        self.size_others += int(msg.size)
                        self.num_others += 1


                except Exception as error:
                    print (" >>>>> ERROR PARSING Packets %s " %pkt, error)


        ## PRINT RESUL
        total = 0
        print("Detected %d MQTT packets" %len(self.packets))
        for t in self.mqtt_types:
            num = len(self.filter_by(t))
            print("--- %d %s " % (num, t))
            total += num
        print("--- TOTAL %d" % (total))

        print('#######################################')
        print('--- Total Message: %d' % self.counter)
        print("--- TCP Message: %s " % self.num_tcp)
        print('--- MQTT Message: %d' % self.num_mqtt)
        print('--- UDP Message: %d' % self.num_upd)
        print('--- OTHER Message: %d' % self.num_others)
        print('#######################################')
        print('--- TCP  packets size: %d' % self.size_tcp)
        print('--- MQTT packets size: %d' % self.size_mqtt)
        print('--- UPD packets size: %d' % self.size_udp)
        print('--- OTHERS packets size: %d' % self.size_others)
        print('--- TOTAL packets size: %d' % (self.size_mqtt + self.size_tcp+ self.size_udp + self.size_others))
        print('#######################################')


    def get_num(self, msg_type):
        return len(self.filter_by(msg_type))

    def filter_by(self, filter):

        output = []
        for pkt in self.packets:
            if pkt.type == filter:
                output.append(pkt)
        return output

    def find_msg_with_id(self, mid, msg_type):
        data = self.filter_by(msg_type)
        for msg in data:
            if msg.mid == mid:
                return msg
        return -1

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
            if mqtt_time > max:
                max = mqtt_time
            if mqtt_time < min:
                min = mqtt_time
            avg_time += mqtt_time
            # print ("%s -- %s " % (repr(msg), repr(msg_pub)))
            counter += 1

        if counter == 0:
            avg_time = 0
        else:
            avg_time /= counter
        print("[E2E] MIN TIME: %s - MAX TIME: %s" % (min, max))
        print("[E2E] The E2E delay for %s is :%f [N. Pkt=%d]" %(msg_type, avg_time, counter))
        return avg_time


    def get_pdr(self):
        filter = self.MQTT_PUB_ACK
        if self.qos == 2:
            filter = self.MQTT_PUB_COM
        data = self.filter_by(filter)

        counter = len(data)
        pdr = (counter / self.num_request) * 100
        print("[PDR] The PDR for [%s] is %f [n. Pkt %d] " % (filter, pdr, counter))
        return pdr

    def get_size(self, protocol):
        if protocol == self.TCP:
            return self.size_tcp
        elif protocol == self.MQTT:
            return self.size_mqtt
        else:
            return 0



    def get_packet_drop(self, paylod_size):
        n_ack = 0
        if self.qos == 1:
            n_ack = self.get_num(self.MQTT_PUB_ACK)
        else:
            n_ack = self.get_num(self.MQTT_PUB_COM)

        size  = self.size_tcp + self.size_mqtt
        if float(size) == 0:
            return 0

        pdrop = (float(n_ack) * float(paylod_size)) / float(size)
        print("[PDROP] The Packet Drop is %f [n. ack: %d  dim: %d] " % (pdrop, n_ack, size))
        return pdrop


    def get_tcp_overhead(self):
        size = self.size_tcp + self.size_mqtt

        if float(size) == 0:
            return 0

        overhead = (self.size_tcp*1.0)/size
        print("[TCP_OVERHEAD] TCP[%d]/TOTAL[%d] = %f " % (self.size_tcp, size, overhead))
        return overhead

##### HERE THE MAIN INFO TO SET UP

#TODO:vanno spostati

N_PACKET_SEND = 250
QoS = 2
PAYLOAD_SIZE = 128
filename = './problem.txt'




def computeTime(json_file, num_test):
    with open(json_file) as file:
        pkts = json.load(file)
        file.close()

    return mqtt_performance(pkts, N_PACKET_SEND, QoS)


if __name__ == '__main__':

    print('#######################################################')
    print("#")
    print("# Analyze Wireshark data for MQTT Performance analysis")
    print("#")
    print('#######################################################')

    json_file = "./test.json"

    with open(json_file) as file:
        pkts = json.load(file)
        file.close()

    demo = mqtt_performance(pkts, N_PACKET_SEND, QoS)
    demo.get_e2e()
    demo.get_pdr()
    demo.get_packet_drop(PAYLOAD_SIZE)
    demo.get_tcp_overhead()
