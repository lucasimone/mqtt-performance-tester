

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
        self.counter = 0
        self.num_mqtt = 0
        self.num_tcp = 0

        self._parse_data()


    def _parse_data(self):

        self.counter = 0
        index = 0  # start_counter
        msg = None
        while index < len(self.data):

            if self.data[index].startswith('Frame'):
                msg = packet()
                try:
                    info = lines[index - 2].split()
                    msg.frame_id = info[1]
                    # TODO: THIS SHOULD BE IMPROVED FOR DIFFERENT TYPE OF MESSAGES
                    msg.type = "".join((info[6], " ", info[7]))
                    msg.size = info[5]
                    msg.protocol = info[4]

                    # Read TIME
                    delta_info = self.data[index + 7].split()
                    msg.delta_time = delta_info[6]
                    epoc_info = self.data[index + 5].split()
                    msg.epoc_time = epoc_info[2]
                except Exception as error:
                    print (" >>>>> ERROR PARSING FILE AT LINE %d" %index )
                ## TO SPEED UP THE PARSER...
                ## TODO: what to do if the file contains not MQTT messages???
                ##index += 20

            elif lines[index].find("Message Identifier") != -1:
                try:
                    msg.mid = self.data[index].split(":")[1].strip()
                except Exception as error:
                    print(" >>>>> ERROR PARSING MID AT LINE %d" % index)
            elif lines[index].startswith("No."):
                self.counter += 1
                self.add_packet(msg)

            index += 1

        ## THIS LINE IS REQUERED TO SAVE THE LAST PACKETS PARSED!!!!!!
        self.add_packet(msg)


        ## PRINT RESUL
        print("Detected %d MQTT packets" %len(self.packets))
        for t in self.mqtt_msg_type:
            print("--- %d %s " % (len(self.filter_by(t)), t))

        print('#######################################')
        print('--- Total Message: %d' % self.counter)
        print("--- TCP Message: %s " % self.num_tcp)
        print('--- MQTT Message: %d' % self.num_mqtt)
        print('#######################################')
        print('--- TCP  packets size: %d' % self.size_tcp)
        print('--- MQTT packets size: %d' % self.size_mqtt)
        print('--- TOTAL packets size: %d' % (self.size_mqtt + self.size_tcp))
        print('#######################################')

    def add_packet(self, msg):

        if msg:
            if msg.protocol == 'TCP':
                self.size_tcp += int(msg.size)
                self.num_tcp += 1

            elif msg.protocol == "MQTT":
                self.num_mqtt += 1
                if msg.type in self.mqtt_msg_type:
                    self.packets.append(msg)
                    #print (repr(msg))
                    self.size_mqtt += int(msg.size)
                else:
                    print ("THIS MQTT MSG IS NOT IN THE LIST %s" %msg.type)
            else:
                print("SKIP Message with protocol %s" % msg.protocol)


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
        pdrop = (float(n_ack) * float(paylod_size)) / float(size)
        print("[PDROP] The Packet Drop is %f [n. ack: %d  dim: %d] " % (pdrop, n_ack, size))


    def get_tcp_overhead(self):
        size = self.size_tcp + self.size_mqtt
        overhead = (self.size_tcp*1.0)/size
        print("[TCP_OVERHEAD] TCP[%d]/TOTAL[%d] = %f " % (self.size_tcp, size, overhead))

##### HERE THE MAIN INFO TO SET UP


print('#######################################################')
print("# Analyze Wireshark data for COAP Performance analysis")
print("# Please insert the file to analyze.")




N_PACKET_SEND = 500
QoS = 1
PAYLOAD_SIZE = 128
filename = './problem.txt'



N_PACKET_SEND = raw_input('N. Request [%d]: ' %N_PACKET_SEND) or N_PACKET_SEND
QoS = raw_input('QoS [%d]: ' %QoS) or QoS
PAYLOAD_SIZE = raw_input('Packet Size (bytes) [%d]: ' %PAYLOAD_SIZE) or PAYLOAD_SIZE

# FILENAME = "coap/dumps/t1_100get.txt"
filename = raw_input('Enter a filename: ') or filename

print('#######################################################')
print(" -- FILENAME {0}".format(filename))
print(" -- N. Packet sent is {0}".format(N_PACKET_SEND))
print(" -- PAYLOAD SIZE {0}".format(PAYLOAD_SIZE))
print(" -- QoS {0}".format(QoS))
print('#######################################')

f = open(filename, 'r')
# f = open(FILENAME, 'r')
lines = f.readlines()
f.close()
demo = mqtt_performance(lines, N_PACKET_SEND, QoS)
demo.get_e2e()
demo.get_pdr()
demo.get_packet_drop(PAYLOAD_SIZE)
demo.get_tcp_overhead()