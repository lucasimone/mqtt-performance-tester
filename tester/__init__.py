_last_capture = None



FILENAME = "data/mqtt_capture"


TMPDIR = "tmp"
DATADIR = "data"
LOGDIR = "log"
BACKUP = "backup"



TEST_RESULT= "data/report.txt"
#PAYLOAD_LIST = [128, 256, 512, 1024]
PAYLOAD_LIST = [128]
<<<<<<< Updated upstream
QoS = [1, 2]
=======
QoS = [1]
>>>>>>> Stashed changes
N_PACKET_SEND = 100
TOPIC = 'topic'


<<<<<<< Updated upstream
IFC = "lo0"
GW_IP = "192.168.42.1"
WAIT_START_TCPDUMP = 1
WAIT_CLOSE_TCPDUMP = 2
TCPDUMP_FILTER =  '' # keep this empty or put ICMP + TCP
=======
IFC = "opensand_tun"
GW_IP = "192.168.42.1"
WAIT_START_TCPDUMP = 1
WAIT_CLOSE_TCPDUMP = 2
TCPDUMP_FILTER =  '' # keep this empty or put ICMP + TCP
>>>>>>> Stashed changes
