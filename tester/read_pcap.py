import re

json_file = "../mqtt_capture_qos_1_payload_1024.json"
print ("######")
STRING_TO_FIND = '{*"_index"'

with open(json_file) as file:
    content = str(file.readlines())


lines = content.replace("', '", "").split("\\n")
counter_mqtt = 0
counter_other = 0

class packet():

    counter = 0


    def __init__(self):
        self.protocol = None
        self.frame_id = None
        self.type = None
        self.size = -1
        self.payload_size = 0
        self.delta_time = -1
        self.epoc_time = -1
        self.mid = -1


    def __repr__(self):
        return "---Pkt mid:%s \tprotocol:%s \tType:%s \tSize:%s \tTime:%s \tEpoc:%s \t Payload Size:%s " \
               %(self.mid, self.protocol, self.type,  self.size, self.delta_time, self.epoc_time, self.payload_size)


mqtt_pkts = []
other_pkt = []


def get(data):
    return data.split()[1].replace('"', "")

def getInt(data):
    val =  get(data)
    return int(val.replace(",",""))

def getFloat(data):
    val = get(data)
    return float(val.replace(",", ""))


pkt = None
for index, l in enumerate(lines):
    if "_index" in l :

        if pkt:
            if pkt.protocol:
                if "mqtt" in pkt.protocol:
                    counter_mqtt += 1
                    mqtt_pkts.append(pkt)
                    print("-n.{0} {1}".format(counter_mqtt, repr(pkt)))
                else:
                    counter_other += 1
                    other_pkt.append(pkt)
                    print("---- OTHER -n.{0} {1}".format(counter_other, repr(pkt)))
            else:
                counter_other += 1
                other_pkt.append(pkt)
                print("---- OTHER -n.{0} {1}".format(counter_other, repr(pkt)))

        pkt = packet()


    elif "frame.protocols" in l:
        pkt.protocol = get(l)
    elif '"mqtt.msgid"' in l:
        if pkt.mid>-1:
            cp_pkt =  pkt
            mqtt_pkts.append(cp_pkt)
            print("-n.{0} {1}".format(counter_mqtt, repr(pkt)))
        pkt.mid = getInt(l)
    elif 'mqtt.len' in l:
        pkt.payload_size = getInt(l)
    elif "frame.time_epoch" in l:
        pkt.epoc_time = getFloat(l)

    elif "frame.time_delta_displayed" in l:
        pkt.delta_time = getFloat(l)

    elif "frame.number" in l:
        pkt.frame_id = get(l)
    elif '"mqtt": {' in l :
        pkt.type = lines[index+1].split('"')[1]

