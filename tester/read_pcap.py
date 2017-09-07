import os
import time
from tester.commands import *
from tester.write_ouput import write_test_result

filename = '../data/mqtt_capture_qos_2_payload_1024.pcap'

#launch_sniffer(filename, IFC, other_filter="")
while not os.path.exists(filename):
    time.sleep(0.001)
    print('.', end='', flush=True)



print()
print("PCAP FILE is READY!")

while os.path.getsize(filename) < 24:
    pass
print("PCAP contains at lease 1 packet")


decode_pcap(filename)
json_filename = os.path.splitext(filename)[0] + '.json'
with open(json_filename) as file:
    pkts = json.load(file)
    file.close()

index = 0
for pkt in pkts:


    if 'mqtt' in pkt["_source"]['layers']:
        msg_type = list(pkt["_source"]['layers']['mqtt'].keys())[0]
        print("Pkt n. {0} - Type: {1}".format(index, msg_type))
        index += 1
        if "Ping" in msg_type:
            print (" CLOSE SNIFFER")
            break



print("FINE PCAP")

#         if eth.type!=dpkt.ethernet.ETH_TYPE_IP:
#             continue
#
#         ip=eth.data
#         ipcounter+=1
#
#         if ip.p==dpkt.ip.IP_PROTO_TCP:
#             tcpcounter+=1
#
#         if ip.p==dpkt.ip.IP_PROTO_UDP:
#             udpcounter+=1
# print ("Total number of packets in the pcap file: ", counter)
# print ("Total number of ip packets: ", ipcounter)
# print ("Total number of tcp packets: ", tcpcounter)
# print ("Total number of udp packets: ", udpcounter)


#
# while counter < 100:
#     counter = 0
#     c_udp = 0
#     try:
#
#         for ts, pkt in dpkt.pcap.Reader(open(filename, 'rb')):
#             eth = dpkt.ethernet.Ethernet(pkt)
#             counter += 1
#
#             # Check whether IP packets: to consider only IP packets
#             if eth.type != dpkt.ethernet.ETH_TYPE_IP:
#                 continue
#                 # Skip if it is not an IP packet
#
#             ip = eth.data
#             if ip.p == dpkt.ip.IP_PROTO_TCP:  # Check for TCP packets
#                 TCP = ip.data
#                 # ADD TCP packets Analysis code here
#             elif ip.p == dpkt.ip.IP_PROTO_UDP:  # Check for UDP packets
#                 UDP = ip.data
#                 c_udp += 1
#                 # UDP packets Analysis code here
#
#     except Exception:
#         print ("Error!")
#     print("PCAP contains {0}  packets".format(counter))
#     print("PCAP contains {0} UDP packets".format(c_udp))
#
# print("END OF READING")

# def print_callback(pkt):
#     print ('Just arrived:', pkt)
#
#
# import pyshark
# capture = pyshark.LiveCapture(interface='en0')
# capture.sniff(timeout=50)
# capture.apply_on_packets(print_callback, timeout=5)
